from mpf.core.custom_code import CustomCode


# Responds to the event "show_score_flash_text"
# Expects 4 text values as event variables (text_1, text_2, text_3, text_4)
# Plays the "score_flash_text" show, where text in displays 1-3 flashes and display 4 does not

# This code exists because show_player cannot read event variables and use them as tokens
# This also enables us to customize the loops value, which is done via a constant, and the events_when_completed
# which will be read from the event.

# Setting for how many loops to execute
# The show is .25 seconds long so 4 loops = 1 second
scoreFlashLoops = 4

class scoreFlash(CustomCode):
    def on_load(self):
        self.machine.events.add_handler('show_score_flash_text', self._show_flash_text)
        self.machine.events.add_handler('show_notify_flash_text', self._show_notify_text)

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



