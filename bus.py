class Bus:

    bus_counter = 0

    def __init__(self, name:str, nominal_kv:float, bus_type:str, vpu:float  = 1.0, delta:float = 0.0):
        valid_bus_types = ["Slack", "PQ", "PV"]

        if bus_type not in valid_bus_types:
            raise ValueError(f"Invalid bus type: {bus_type}")

        self.name = name
        self.nominal_kv = nominal_kv
        self.vpu = vpu
        self.delta = delta
        self.bus_type = bus_type

        self.bus_index = Bus.bus_counter
        Bus.bus_counter += 1

