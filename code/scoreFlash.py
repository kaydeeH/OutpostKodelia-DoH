from mpf.core.custom_code import CustomCode


# Responds to the event "attract_show_last_game_scores"
# This code exists because who knows how many players were in the last game

# Setting for how many loops to execute
# The show is .25 seconds long so 4 loops = 1 second
scoreFlashLoops = 4
hs_show_instance = None

class scoreFlash(CustomCode):
    def on_load(self):
        self.info_log('ScoreFlash controller successfully loaded!!')
        self.machine.events.add_handler('show_score_flash_text', self._show_flash_text)
        self.machine.events.add_handler('show_notify_flash_text', self._show_notify_text)
        self.machine.events.add_handler('segment_high_score_enter_initials', self._show_enter_initials)
        self.machine.events.add_handler('high_score_award_display', self._handle_segment_award_display)
        self.machine.events.add_handler('kodelia_tilt_warn', self._handle_tilt_warning)
        self.machine.events.add_handler('kodelia_tilt', self._handle_tilt)
        self.machine.events.add_handler('boars_nest_show_bonus_text', self._boars_bonus_text)

    def _show_flash_text(self, **kwargs):
        show_tokens = {"text_1": kwargs.get("text_1"), "text_2": kwargs.get("text_2"), "text_3": kwargs.get("text_3"),
                       "text_4": kwargs.get("text_4")}
        events_when_completed = {kwargs.get("events_when_completed")}
        show_instance = self.machine.shows["score_flash_text"].play(loops=scoreFlashLoops, show_tokens=show_tokens,
                                                                    events_when_completed=events_when_completed)

    def _show_notify_text(self, **kwargs):
        show_tokens = {"text_1": kwargs.get("text_1"), "text_2": kwargs.get("text_2"), "text_3": kwargs.get("text_3"),
                       "text_4": kwargs.get("text_4")}
        events_when_completed = {kwargs.get("events_when_completed")}
        show_instance = self.machine.shows["notify_flash_text"].play(loops=scoreFlashLoops, show_tokens=show_tokens,
                                                                    events_when_completed=events_when_completed)

    def _show_enter_initials(self, **kwargs):
        show_tokens = {"text_1": "Player" + str(kwargs.get("player_num")), "text_2": kwargs.get("award"), "text_3": "  Name>"}
        self.hs_show_instance = self.machine.shows["hs_initial_entry"].play(show_tokens=show_tokens)

    def _handle_segment_award_display(self, **kwargs):
        self.hs_show_instance.stop()

    def _handle_tilt_warning(self, **kwargs):
        show_tokens = {"danger_count": str(kwargs.get("count"))}
        show_instance = self.machine.shows["kodelia_tilt_warn"].play(loops=scoreFlashLoops, show_tokens=show_tokens)

    def _handle_tilt(self, **kwargs):
        show_instance = self.machine.shows["kodelia_tilt"].play(loops=scoreFlashLoops)

    def _boars_bonus_text(self, **kwargs):
        show_tokens = {"boar_score_pre": str(kwargs.get("boar_score_pre")), "score_type": str(kwargs.get("score_type")),
                       "score_value": str(kwargs.get("score_value")),
                       "boar_score_post": str(kwargs.get("boar_score_post"))}
        events_when_completed = {kwargs.get("events_when_completed")}
        show_instance = self.machine.shows["boar_bonus_display"].play(show_tokens=show_tokens, loops=0,
                                                                      events_when_completed=events_when_completed)
