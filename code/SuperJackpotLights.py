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
    random_light_count = 40
    alternator = 0

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
        self.machine.events.post('dim_for_super_jackpot')
        self.machine.delay.add(callback=self._continue_handle, ms=1000)

    def _continue_handle(self):
        jackpot_lights = self._get_random_lights()  # type: List[Light]
        # self.machine.events.post('super_jackpot_lights_available_' + str(len(self.lights)))
        kwargs = {'lights': jackpot_lights}
        if self.creek_scored == 1 and self.hazzard_scored == 1:
            self.machine.events.post('jackpot_light_both')
            self._double_jackpot(**kwargs)
        else:
            if self.creek_scored == 1:
                self.machine.events.post('jackpot_light_creek_only')
                self._creek_jackpot(**kwargs)

            if self.hazzard_scored == 1:
                self.machine.events.post('jackpot_light_hazzard_only')
                self._hazzard_jackpot(**kwargs)

    def _reset(self, **kwargs):
        del kwargs
        self.creek_scored = 0
        self.hazzard_scored = 0

    def _creek_jackpot(self, **kwargs):
        if 'light' in kwargs:
            last_light = kwargs.get('light')
            last_light.remove_from_stack_by_key("jackpot", 50)

        lights = kwargs.get('lights')
        if len(lights) > 0:
            jackpot_light = lights.pop(0)
            self.machine.events.post('jackpot_light_firing_creek_' + jackpot_light.name)

            if self.alternator == 0:
                jackpot_light.color('white', 0, 3000, 'jackpot')
                self.alternator = 1
            else:
                jackpot_light.color('2E8B57', 0, 3000, 'jackpot')
                self.alternator = 0
            del kwargs
            kwargs = {'lights': lights, 'light': jackpot_light}
            self.machine.delay.add(callback=self._creek_jackpot, ms=50, **kwargs)
        else:
            self.machine.events.post('dim_for_super_jackpot_end')

    def _double_jackpot(self, **kwargs):
        if 'light' in kwargs:
            last_light = kwargs.get('light')
            last_light.remove_from_stack_by_key("jackpot", 50)

        lights = kwargs.get('lights')
        if len(lights) > 0:
            jackpot_light = lights.pop(0)
            self.machine.events.post('jackpot_light_firing_double_' + jackpot_light.name)

            if self.alternator == 0:
                jackpot_light.color('white', 0, 3000, 'jackpot')
                self.alternator = 1
            else:
                if self.alternator == 1:
                    jackpot_light.color('FF7500', 0, 3000, 'jackpot')
                    self.alternator = 2
                else:
                    jackpot_light.color('2E8B57', 0, 3000, 'jackpot')
                    self.alternator = 0
            del kwargs
            kwargs = {'lights': lights, 'light': jackpot_light}
            self.machine.delay.add(callback=self._double_jackpot, ms=50, **kwargs)
        else:
            self.machine.events.post('dim_for_super_jackpot_end')

    def _hazzard_jackpot(self, **kwargs):
        if 'light' in kwargs:
            last_light = kwargs.get('light')
            last_light.remove_from_stack_by_key("jackpot", 50)

        lights = kwargs.get('lights')
        if len(lights) > 0:
            jackpot_light = lights.pop(0)
            self.machine.events.post('jackpot_light_firing_hazzard_' + jackpot_light.name)

            if self.alternator == 0:
                jackpot_light.color('white', 0, 3000, 'jackpot')
                self.alternator = 1
            else:
                jackpot_light.color('FF7500', 0, 3000, 'jackpot')
                self.alternator = 0
            del kwargs
            kwargs = {'lights': lights, 'light': jackpot_light}
            self.machine.delay.add(callback=self._hazzard_jackpot, ms=50, **kwargs)
        else:
            self.machine.events.post('dim_for_super_jackpot_end')

    def _get_random_lights(self):
        rando_lights = list()
        sample = random.sample(range(1, len(self.lights)), self.random_light_count)
        for item in sample:
            rando_lights.append(self.lights[item])
        return rando_lights


