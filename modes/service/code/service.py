from mpf.modes.service.code.service import Service
import subprocess
import os
from collections import namedtuple
from functools import partial

from typing import List

from mpf.core.async_mode import AsyncMode
from mpf.core.switch_controller import MonitoredSwitchChange
from mpf.core.utility_functions import Util

ServiceMenuEntry = namedtuple("ServiceMenuEntry", ["label", "callback"])

class Service(Service):

    # def _load_menu_entries(self) -> List[ServiceMenuEntry]:
    #     """Return the menu items with label and callback."""
    #     # If you want to add menu entries overload the mode and this method.
    #     entries = [
    #         ServiceMenuEntry("Diagnostics Menu", self._diagnostics_menu),
    #         ServiceMenuEntry("Audits Menu", self._audits_menu),
    #         ServiceMenuEntry("Adjustments Menu", self._adjustments_menu),
    #         ServiceMenuEntry("Utilities Menu", self._utilities_menu),
    #         ServiceMenuEntry("Dumb Stuff Menu", self._utilities_menu),
    #     ]
    #     return entries

    def _load_diagnostic_light_menu_entries(self) -> List[ServiceMenuEntry]:
        """Return the light menu items with label and callback."""
        entries = [
            ServiceMenuEntry("Single Light Test", self._light_test_menu),
            ServiceMenuEntry("All Light Test", self._light_test_all),
            ServiceMenuEntry("Light Channel Test", self._fc_channel_test)
        ]
        return entries

    async def _light_test_all(self):
        position = 0
        color_position = 0
        colors = ["white", "red", "green", "blue", "yellow"]
        items = self.machine.service.get_light_map()

        # do not crash if no lights are configured
        if not items:   # pragma: no cover
            return

        self.machine.events.post("kodelia_service_menu_flash_all_lights", test_color=colors[color_position])
        self.machine.events.post("service_light_all_test_start", test_color=colors[color_position])

        while True:
            key = await self._get_key()
            if key == 'ESC':
                self.machine.events.post("kodelia_service_menu_flash_all_lights_stop")
                break
            # if key == 'UP':
            #     # do nothing
            # elif key == 'DOWN':
            #     # do nothing
            elif key == 'ENTER':
                # change color
                color_position += 1
                if color_position >= len(colors):
                    color_position = 0
                self.machine.events.post("kodelia_service_menu_flash_all_lights", test_color=colors[color_position])
                self.machine.events.post("service_light_all_test_start", test_color=colors[color_position])

        self.machine.events.post("service_light_all_test_stop")

    async def _fc_channel_test(self):
        position = 0
        color_position = 0
        colors = ["white", "red", "green", "blue", "yellow"]
        fchan = ["j3", "j4", "j5", "j7", "j8", "j9", "j10", "disp1led", "disp2led", "disp3led", "disp4led", "disp5led", ]

        self.machine.events.post("kodelia_service_menu_flash_channel", test_color=colors[color_position], test_channel=fchan[position])
        self.machine.events.post("service_light_channel_test_start", test_color=colors[color_position], test_channel=fchan[position])

        while True:
            key = await self._get_key()
            if key == 'ESC':
                self.machine.events.post("kodelia_service_menu_flash_channel_lights_stop")
                break
            if key == 'UP':
                position += 1
                if position >= len(fchan):
                    position = 0
            elif key == 'DOWN':
                position -= 1
                if position < 0:
                    position = len(fchan) - 1
            elif key == 'ENTER':
                # change color
                color_position += 1
                if color_position >= len(colors):
                    color_position = 0
            self.machine.events.post("kodelia_service_menu_flash_channel", test_color=colors[color_position], test_channel=fchan[position])
            self.machine.events.post("service_light_channel_test_start", test_color=colors[color_position], test_channel=fchan[position])

        self.machine.events.post("service_light_channel_test_stop")