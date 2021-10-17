from mpf.core.custom_code import CustomCode


# Responds to the event "show_score_flash_text"
# Expects 4 text values as event variables (text_1, text_2, text_3, text_4)
# Plays the "score_flash_text" show, where text in displays 1-3 flashes and display 4 does not

# This code exists because show_player cannot read event variables and use them as tokens
# This also enables us to customize the loops value, which is done via a constant, and the events_when_completed
# which will be read from the event.

# Setting for how many loops to execute
# The show is 1 second long so 4 loops = 1 second
displayLoops = 5

class atrRecentScores(CustomCode):
    def on_load(self):
        self.info_log('atrHighScores controller successfully loaded!!')
        self.machine.events.add_handler('attract_show_last_game_scores', self._show_recent_scores)

    def _show_recent_scores(self, **kwargs):
        sc1 = str(self.machine.variables.get_machine_var("player_1_score"))
        if sc1 == "None":
            sc1 = "0"
        sc2 = str(self.machine.variables.get_machine_var("player_2_score"))
        if sc2 == "None":
            sc2 = ""
        sc3 = str(self.machine.variables.get_machine_var("player_3_score"))
        if sc3 == "None":
            sc3 = ""
        sc4 = str(self.machine.variables.get_machine_var("player_4_score"))
        if sc4 == "None":
            sc4 = ""

        show_tokens = {"atr_score1": sc1, "atr_score2": sc2, "atr_score3": sc3,
                       "atr_score4": sc4}
        show_instance = self.machine.shows["attract_last_game_scores"].play(loops=displayLoops, show_tokens=show_tokens,
                                                                            priority=15)




