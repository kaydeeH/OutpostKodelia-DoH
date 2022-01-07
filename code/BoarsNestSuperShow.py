import time
from typing import List

from mpf.core.custom_code import CustomCode
from mpf.devices.light import Light
from mpf.core.device_manager import DeviceCollection
import random


class BoarsNestSuperShow(CustomCode):

    lights = None  # type: DeviceCollection[str, Light]
    creek_scored = 1
    hazzard_scored = 1
    random_light_count = 66
    alternator = 0
    color_green = '2E8B57'
    color_orange = 'FF7500'

    def on_load(self):
        self.info_log('SuperJackpotLight controller successfully loaded!!')
        BoarsNestSuperShow.lights = self.machine.lights.items_tagged('superjack')
        self.machine.events.add_handler('boars_nest_super_show', self._handle_jackpot)

    def _handle_jackpot(self, **kwargs):
        del kwargs
        jackpot_lights = self._get_random_lights()  # type: List[Light]
        kwargs = {'lights': jackpot_lights, 'type': 'both'}
        self._jackpot(**kwargs)

    def _reset(self, **kwargs):
        del kwargs
        self.creek_scored = 1
        self.hazzard_scored = 1
        self.alternator = 0

    def _get_random_lights(self):
        rando_lights = list()
        sample = random.sample(range(1, len(self.lights)), self.random_light_count)
        for item in sample:
            rando_lights.append(self.lights[item])
        return rando_lights

    def _jackpot(self, **kwargs):
        # turn off the previous light, if there was one
        if 'last_light' in kwargs:
            last_light = kwargs.get('last_light')
            last_light.remove_from_stack_by_key("jackpot", 75)

        # process the remaining lights
        lights = kwargs.get('lights')
        jackpot_type = kwargs.get('type')

        # if any lights remain
        if len(lights) > 0:
            # pop the next light off the list and process it
            jackpot_light = lights.pop(0)
            self.machine.events.post('jackpot_light_firing_' + jackpot_type + '_' + jackpot_light.name)

            # based on alternator value and jackpot type, fire the light the appropriate color:
            # creek - alternate between white and green
            # hazzard - alternate between white and orange
            # both - alternate between white, green, and orange
            if self.alternator == 0:
                jackpot_light.color('white', 0, 60000, 'jackpot')
                self.alternator = 1

            elif self.alternator == 1:
                if jackpot_type == 'creek' or jackpot_type == 'both':
                    color2 = self.color_green
                else:  # jackpot_type == 'hazzard'
                    color2 = self.color_orange

                jackpot_light.color(color2, 0, 60000, 'jackpot')

                # pick the appropriate next alternator value based on type
                if jackpot_type == 'both':
                    self.alternator = 2
                else: # creek or hazzard
                    self.alternator = 0
            else:  # alternator == 2
                jackpot_light.color(self.color_orange, 0, 60000, 'jackpot')
                self.alternator = 0

            # rebuild the kwargs and call back to this same function after the desire delay
            del kwargs
            kwargs = {'lights': lights, 'last_light': jackpot_light, 'type': jackpot_type}
            self.machine.delay.add(callback=self._jackpot, ms=75, **kwargs)

        else:  # no lights remain
            self._reset()
