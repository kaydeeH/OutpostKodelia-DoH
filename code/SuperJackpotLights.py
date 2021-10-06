import time
from typing import List

from mpf.core.custom_code import CustomCode
from mpf.devices.light import Light
from mpf.core.device_manager import DeviceCollection
import random


class SuperJackpotLights(CustomCode):

    lights = None  # type: DeviceCollection[str, Light]
    creek_scored = 0
    hazzard_scored = 0
    random_light_count = 20

    def on_load(self):
        self.info_log('SuperJackpotLight controller successfully loaded!!')
        SuperJackpotLights.lights = self.machine.lights.items_tagged('superjack')
        self.machine.events.add_handler('creek_super_jackpot_enabled', self._handle_creek)
        self.machine.events.add_handler('hazzard_super_jackpot_enabled', self._handle_hazzard)
        self.machine.events.add_handler('s_waterfall_rollover_active', self._handle_jackpot)
        self.machine.events.add_handler('ball_will_end', self._reset)

    def _handle_creek(self, **kwargs):
        del kwargs
        self.creek_scored = 1
        self.machine.events.post('super_jackpot_monitor_creek_enabled')

    def _handle_hazzard(self, **kwargs):
        del kwargs
        self.hazzard_scored = 1
        self.machine.events.post('super_jackpot_monitor_hazzard_enabled')

    def _handle_jackpot(self, **kwargs):
        del kwargs
        kwargs = {"creek": self.creek_scored, "hazzard": self.hazzard_scored}
        self.machine.events.post('super_jackpot_monitor_jackpot_scored', **kwargs)
        if self.creek_scored == 1 and self.hazzard_scored == 1:
            self._double_jackpot()
        else:
            if self.creek_scored == 1:
                self._creek_jackpot()

            if self.hazzard_scored == 1:
                self._hazzard_jackpot()

    def _reset(self, **kwargs):
        del kwargs
        SuperJackpotLights.creek_scored = 0
        SuperJackpotLights.hazzard_scored = 0

    def _double_jackpot(self):
        jackpot_lights = self._get_random_lights()  # type: List[Light]
        alternator = 0
        for jackpot_light in jackpot_lights:
            self.machine.events.post('jackpot_light_firing_both_' + jackpot_light.name)
            if alternator == 0:
                jackpot_light.color('white', 0, 3000, 'jackpot')
                alternator = 1
            else:
                if alternator == 1:
                    jackpot_light.color('FF7500', 0, 3000, 'jackpot')
                    alternator = 2
                else:
                    jackpot_light.color('2E8B57', 0, 3000, 'jackpot')
                    alternator = 0

            time.sleep(0.01)
            jackpot_light.remove_from_stack_by_key("jackpot", 50)
            time.sleep(0.05)

    def _creek_jackpot(self):
        self.machine.events.post('jackpot_light_creek_only')
        jackpot_lights = self._get_random_lights()  # type: List[Light]
        alternator = 0
        for jackpot_light in jackpot_lights:
            self.machine.events.post('jackpot_light_firing_creek_' + jackpot_light.name)
            if alternator == 0:
                jackpot_light.color('white', 0, 3000, 'jackpot')
                alternator = 1
            else:
                jackpot_light.color('2E8B57', 0, 3000, 'jackpot')
                alternator = 0
            time.sleep(0.01)
            jackpot_light.remove_from_stack_by_key("jackpot", 50)
            time.sleep(0.05)

    def _hazzard_jackpot(self):
        jackpot_lights = self._get_random_lights()  # type: List[Light]
        alternator = 0
        for jackpot_light in jackpot_lights:
            self.machine.events.post('jackpot_light_firing_hazzard_' + jackpot_light.name)
            if alternator == 0:
                jackpot_light.color('white', 0, 3000, 'jackpot')
                alternator = 1
            else:
                jackpot_light.color('FF7500', 0, 3000, 'jackpot')
                alternator = 0
            time.sleep(0.01)
            jackpot_light.remove_from_stack_by_key("jackpot", 50)
            time.sleep(0.05)

    def _get_random_lights(self):
        rando_lights = list()
        sample = random.sample(range(1, len(self.lights)), self.random_light_count)
        for item in sample:
            rando_lights.append(self.lights[item])
        return rando_lights


