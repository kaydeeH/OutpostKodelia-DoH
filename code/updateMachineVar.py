from mpf.core.custom_code import CustomCode


class updateMachineVar(CustomCode):
    def on_load(self):
        self.machine.events.add_handler('update_display_1', self._updateDisp1)
        self.machine.events.add_handler('update_display_2', self._updateDisp2)
        self.machine.events.add_handler('update_display_3', self._updateDisp3)
        self.machine.events.add_handler('update_display_4', self._updateDisp4)
        self.machine.events.add_handler('update_display_5', self._updateDisp5)

    def _updateDisp1(self, **kwargs):
        self.machine.variables.set_machine_var("disp1value", kwargs.get("text"))

    def _updateDisp2(self, **kwargs):
        self.machine.variables.set_machine_var("disp2value", kwargs.get("text"))

    def _updateDisp3(self, **kwargs):
        self.machine.variables.set_machine_var("disp3value", kwargs.get("text"))

    def _updateDisp4(self, **kwargs):
        self.machine.variables.set_machine_var("disp4value", kwargs.get("text"))

    def _updateDisp5(self, **kwargs):
        self.machine.variables.set_machine_var("disp5value", kwargs.get("text"))

