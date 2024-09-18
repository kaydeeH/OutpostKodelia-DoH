"""Contains the High Score mode code."""
from mpf.modes.high_score.code.high_score import HighScore
import asyncio

from mpf.core.async_mode import AsyncMode
from mpf.core.player import Player


class HighScore(HighScore):

    charListInit = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
                "V", "W", "X", "Y", "Z", "<", "*"]
    charListEnd = ["*", "<"]
    charListCurrent = charListInit
    charEntry = "A"
    charPos = 0     # position in the charList
    charChoice = 0  # position in the overall input

    def mode_init(self):
        """Initialise high score mode."""
        self.data_manager = self.machine.create_data_manager('high_scores')
        self.high_scores = self.data_manager.get_data()

        self.high_score_config = self.machine.config_validator.validate_config(
            config_spec='high_score',
            source=self.config.get('high_score', {}),
            section_name='high_score')

        # if data is invalid. do not use it
        if self.high_scores and not self._validate_data(self.high_scores):
            self.log.warning("High score data failed validation. Resetting to defaults.")
            self.high_scores = None

        # Load defaults if no high_scores are stored
        if not self.high_scores:
            self._load_defaults()

        self._create_machine_vars()
        self.pending_award = None

        for event in self.high_score_config['reset_high_scores_events']:
            # important: this may not be a mode handler as it should be always active
            self.machine.events.add_handler(event, self._reset)

        # this is the new code, above is original code, prob should just call the Super class method instead of copying
        self.machine.events.add_handler('segment_high_score_left', self._handle_high_score_left)
        self.machine.events.add_handler('segment_high_score_right', self._handle_high_score_right)
        self.machine.events.add_handler('segment_high_score_next', self._handle_high_score_enter)
        self.machine.events.add_handler('hs_entry_force_reset', self._reset_hs_entry)
        self.machine.variables.set_machine_var("doh_hs_entry", "A")

    def _reset_hs_entry(self, **kwargs):
        self.machine.variables.set_machine_var("doh_hs_entry", "A")

    def _handle_high_score_left(self, **kwargs):
        if self.charPos == 0:
            self.charPos = len(self.charListCurrent) - 1
        else:
            self.charPos = self.charPos - 1

        if self.charChoice == 0:
            self.charEntry = self.charListCurrent[self.charPos]
        else:
            self.charEntry = self.charEntry[0:self.charChoice] + self.charListCurrent[self.charPos]
        self.machine.variables.set_machine_var("doh_hs_entry", self.charEntry)

    def _handle_high_score_right(self, **kwargs):
        if self.charPos == len(self.charListCurrent) - 1:
            self.charPos = 0
        else:
            self.charPos = self.charPos + 1

        self.charEntry = self.charEntry[0:self.charChoice] + self.charListCurrent[self.charPos]
        self.machine.variables.set_machine_var("doh_hs_entry", self.charEntry)

    def _handle_high_score_enter(self, **kwargs):
        if self.charListCurrent[self.charPos] == "*":
            if self.charEntry[len(self.charEntry)-1] == "*":
                self.charEntry = self.charEntry[0:len(self.charEntry)-1]
            self.machine.events.post('text_input_high_score_complete',
                                     text=self.charEntry)
        else:
            if self.charListCurrent[self.charPos] == "<":
                if self.charChoice != 0:
                    self.charEntry = self.charEntry[0:self.charChoice-1]
                    self.charChoice = self.charChoice - 1
                    self.charListCurrent = self.charListInit
                    self.charPos = len(self.charListCurrent) - 2
                    self.charEntry = self.charEntry[0:self.charChoice] + self.charListCurrent[self.charPos]
            else:
                self.charEntry = self.charEntry[0:self.charChoice] + self.charListCurrent[self.charPos]
                if self.charChoice == 5:
                    self.charListCurrent = self.charListEnd
                    self.charPos = 0
                else:
                    self.charListCurrent = self.charListInit
                self.charChoice = self.charChoice + 1
                self.charEntry = self.charEntry[0:self.charChoice] + self.charListCurrent[self.charPos]
        self.machine.variables.set_machine_var("doh_hs_entry", self.charEntry)

    async def _ask_player_for_initials(self, player: Player, award_label: str, value: int, category_name: str) -> str:
        """Show text widget to ask player for initials."""
        self.info_log("New high score. Player: %s, award_label: %s"
                      ", Value: %s", player, award_label, value)

        # reset in case not the first time today
        self.charEntry = "A"
        self.charPos = 0  # position in the charList
        self.charChoice = 0  # position in the overall input

        self.machine.events.post('segment_high_score_enter_initials',
                                 #award=award_label,
                                 award=award_label,
                                 player_num=player.number,
                                 value=value)

        event_result = await asyncio.wait_for(
            self.machine.events.wait_for_event("text_input_high_score_complete"),
            timeout=self.high_score_config['enter_initials_timeout']
        )   # type: dict

        return event_result["text"] if "text" in event_result else ''