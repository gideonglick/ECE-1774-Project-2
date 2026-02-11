class Generator:
    def __init__(self, name: str, bus1_name, voltage_setpoint:float, mw_setpoint: float):
        self.name = name
        self.bus1_name = bus1_name
        self.voltage_setpoint = voltage_setpoint
        self.mw_setpoint = mw_setpoint

