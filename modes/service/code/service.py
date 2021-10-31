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

    ksLast = ""
    ksLastList = []

    # If a title is on this list, it will not be added to the breadcrumb trail
    ksSkipList = ["Switch Edge Test", "Single Coil Test", "Single Light Test", "Light Channel Test", "All Light Test",
                  "Earning Audits", "Switch Audits", "Shot Audits", "Event Audits", "Player Audits",
                  "Standard Adjustments", "Feature Adjustments", "Game Adjustments", "Coin Adjustments",
                  "Reset Coin Audits", "Reset Game Audits", "Reset High Scores", "Reset Credits",
                  "Reset to Factory Settings"]

    def _ks_purge_list(self):
        self.ksLastList = []

    def _ks_add_to_list(self, last_item: str):
        if not(last_item in self.ksSkipList):
            self.ksLastList.insert(len(self.ksLastList), last_item)

    def _ks_pop_from_list(self):
        if len(self.ksLastList) > 0:
            self.ksLastList.pop(len(self.ksLastList)-1)

    def _ks_provide_list(self):
        ret_string = ""
        for nav in self.ksLastList:
            if ret_string == "":
                ret_string = nav
            else:
                ret_string = ret_string + ">" + nav
        return ret_string

    def _load_diagnostic_light_menu_entries(self) -> List[ServiceMenuEntry]:
        """Return the light menu items with label and callback."""
        entries = [
            ServiceMenuEntry("Single Light Test", self._light_test_menu),
            ServiceMenuEntry("All Light Test", self._light_test_all),
            ServiceMenuEntry("Light Channel Test", self._fc_channel_test)
        ]
        return entries

    def _update_main_menu(self, items: List[ServiceMenuEntry], position: int):
        self.machine.events.post("service_menu_deselected")
        self.machine.events.post("service_menu_show")
        self.machine.events.post("service_menu_selected", label=items[position].label, ks_last=self._ks_provide_list())

    def _load_menu_entries(self) -> List[ServiceMenuEntry]:
        """Return the menu items with label and callback."""
        # If you want to add menu entries overload the mode and this method.
        self._ks_purge_list()
        entries = [
            ServiceMenuEntry("Diagnostics Menu", self._diagnostics_menu),
            ServiceMenuEntry("Audits Menu", self._audits_menu),
            ServiceMenuEntry("Adjustments Menu", self._adjustments_menu),
            ServiceMenuEntry("Utilities Menu", self._utilities_menu),

        ]
        self.ksLast = ""
        return entries

    async def _make_menu(self, items):
        """Show a menu by controlling slides via events and executing callbacks."""
        if not items:
            # do not crash on empty menu
            return
        position = 0
        self._update_main_menu(items, position)

        while True:
            key = await self._get_key()
            if key == 'ESC':
                self._ks_pop_from_list()
                return
            if key == 'UP':
                position += 1
                if position >= len(items):
                    position = 0
                self._update_main_menu(items, position)
            elif key == 'DOWN':
                position -= 1
                if position < 0:
                    position = len(items) - 1
                self._update_main_menu(items, position)
            elif key == 'ENTER':
                # call submenu
                self._ks_add_to_list(items[position].label)
                await items[position].callback()
                self._update_main_menu(items, position)

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

    # Adjustments
    def _load_adjustments_menu_entries(self) -> List[ServiceMenuEntry]:
        """Return the adjustments menu items with label and callback."""
        return [
            ServiceMenuEntry("Standard Adjustments", partial(self._settings_menu, "standard")),
            ServiceMenuEntry("Feature Adjustments", partial(self._settings_menu, "feature")),
            ServiceMenuEntry("Game Adjustments", partial(self._settings_menu, "game")),
            ServiceMenuEntry("Coin Adjustments", partial(self._settings_menu, "coin")),
            ServiceMenuEntry("Coil Power Adjustments", partial(self._settings_menu, "coilpower"))
        ]

