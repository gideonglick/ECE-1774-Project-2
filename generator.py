from settings import Settings

class Generator:
    def __init__(self, name: str, bus1_name: str, voltage_setpoint: float, mw_setpoint: float, settings: Settings,
                 xd_subtransient: float = 0.0):
        self.name = name
        self.bus1_name = bus1_name
        self.voltage_setpoint = voltage_setpoint
        self.mw_setpoint = mw_setpoint
        self.settings = settings
        self.xd_subtransient = xd_subtransient  # subtransient reactance in per unit
        self.p = self.calc_p()

    def calc_p(self):
        return self.mw_setpoint / self.settings.sbase
