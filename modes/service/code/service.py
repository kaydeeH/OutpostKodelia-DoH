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

        for item in items:
            item.light.color(colors[color_position], key="service", priority=1000000)
#            self.machine.show_player.play()
        key = await self._get_key()
        for item in items:
            item.light.remove_from_stack_by_key("service")