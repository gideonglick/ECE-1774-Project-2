class Bus:

    bus_counter = 0

    def __init__(self, name:str, nominal_kv:float):
        """
        :param name:
        :param nominal_kv:
        """
        self.name = name
        self.nominal_kv = nominal_kv

        self.bus_index = Bus.bus_counter
        Bus.bus_counter += 1

