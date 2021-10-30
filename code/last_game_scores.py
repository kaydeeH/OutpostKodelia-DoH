from mpf.core.custom_code import CustomCode

# This code exists because you cannot check to see if a machine variable exists within MPF YAML
# It would seem that any evaluation using a variable that doesn't exist, like
# machine.player4_score after a 3 player game, would always evaluate to false,
# yet displaying this value would result in a zero being displayed

class LastGameScores(CustomCode):

    def on_load(self):
        self.machine.events.add_handler('attract_previous_scores', self._generate_events, 10000)

    def _generate_events(self, **kwargs):
        del kwargs

        player2 = self.machine.variables.get_machine_var("player2_score")
        player3 = self.machine.variables.get_machine_var("player3_score")
        player4 = self.machine.variables.get_machine_var("player4_score")

        if player2:
            self.machine.events.post('lastgame_player2', score=player2)
        else:
            self.machine.events.post('lastgame_player2_blank')

        if player3:
            self.machine.events.post('lastgame_player3', score=player3)
        else:
            self.machine.events.post('lastgame_player3_blank')

        if player4:
            self.machine.events.post('lastgame_player4', score=player4)
        else:
            self.machine.events.post('lastgame_player4_blank')
