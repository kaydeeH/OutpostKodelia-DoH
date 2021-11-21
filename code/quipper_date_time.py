from mpf.core.custom_code import CustomCode
from datetime import date
import time


class quipperDT(CustomCode):

    quickstarts = 0

    def on_load(self):
        self.info_log('quipperDT controller successfully loaded!!')
        self.machine.events.add_handler('quipper_initial_dttm_check', self._quipper_dttm_check)

    def _quipper_dttm_check(self, **kwargs):
        quip_found = False

        # Check the last game timer
        if self.machine.timers.quipper_time_since_end.running and self.machine.timers.quipper_time_since_end.ticks < 21:
            self.quickstarts = self.quickstarts + 1
        else:
            self.quickstarts = 0
        self.machine.events.post('quipper_timer_stop')
        if self.quickstarts > 1:
            self.quickstarts = 0
            self.machine.events.post('quipper_quick_start')
            quip_found = True

        today = date.today()
        seconds = time.time()
        tresult = time.localtime(seconds)

        hour = tresult.tm_hour

        # late night game start
        if hour == 22 or hour == 23 and not quip_found:
            quip_found = True
            self.machine.events.post('quipper_late_night_game_start')

        # midnight hour
        if hour == 0 and not quip_found:
            quip_found = True
            self.machine.events.post('quipper_midnight_hour_start')

        # early morning
        if hour > 0 and hour < 6 and not quip_found:
            quip_found = True
            self.machine.events.post('quipper_early_morning_game_start')

        # FRIDAY check
        if today.weekday() == 4 and not quip_found:
            quip_found = True
            self.machine.events.post('quipper_friday_game_start')

        # CHRISTMAS check
        if today.day == 25 and today.month == 12 and not quip_found:
            quip_found = True
            self.machine.events.post('quipper_christmas_game_start')

        # APRIL FOOLS DAY check
        if today.day == 1 and today.day == 4 and not quip_found:
            quip_found = True
            self.machine.events.post('quipper_april_fools_game_start')

        # nothing left
        if not quip_found:
            quip_found = True
            self.machine.events.post('quipper_no_time_day_game_start')
