from typing import Dict, List, Optional
from bus import Bus
from load import Load
from generator import Generator
from transformer import Transformer
from transmissionLine import TransmissionLine

class Circuit:

    def __init__(self, name : str):
        self.name = name
        self.buses: Dict[str, Bus] = {}
        self.loads: Dict[str, Load] = {}
        self.generators: Dict[str, Generator] = {}
        self.transmission_lines: Dict[str, TransmissionLine] = {}
        self.transformers: Dict[str, Transformer] = {}

    def add_bus(self, name: str, nominal_kv: float):
        if name in self.buses:
            raise ValueError(f"bus {name} already exists")
        self.buses[name] = Bus(name, nominal_kv)

    def add_transformer(self, name: str, bus1_name: str, bus2_name: str, r: float, x: float):
        if name in self.transformers:
            raise ValueError(f"transformer {name} already exists")
        if bus1_name not in self.buses.keys():
            raise ValueError(f"bus {bus1_name} does not exist")
        if bus2_name not in self.buses.keys():
            raise ValueError(f"bus {bus2_name} does not exist")
        if bus1_name == bus2_name:
            raise ValueError("transformer cannot connect a bus to itself")

        self.transformers[name] = Transformer(name, bus1_name, bus2_name, r, x)

    def add_transmission_line(self, name:str, bus1_name:str, bus2_name:str, r:float, x:float, g:float, b:float):
        if name in self.transmission_lines:
            raise ValueError(f"transmission_line {name} already exists")
        if bus1_name not in self.buses.keys():
            raise ValueError(f"bus {bus1_name} does not exist")
        if bus2_name not in self.buses.keys():
            raise ValueError(f"bus {bus2_name} does not exist")
        if bus1_name == bus2_name:
            raise ValueError("transmission line cannot connect a bus to itself")

        self.transmission_lines[name] = TransmissionLine(name, bus1_name, bus2_name, r, x, g, b)

    def add_generator(self, name: str, bus1_name, voltage_setpoint:float, mw_setpoint: float):
        if name in self.generators:
            raise ValueError(f"generator {name} already exists")
        if bus1_name not in self.buses.keys():
            raise ValueError(f"bus {bus1_name} does not exist")

        self.generators[name] = Generator(name, bus1_name, voltage_setpoint, mw_setpoint)

    def add_load(self, name: str, bus1_name: str, mw:float, mvar:float):
        if name in self.loads:
            raise ValueError(f"load {name} already exists")
        if bus1_name not in self.buses.keys():
            raise ValueError(f"bus {bus1_name} does not exist")

        self.loads[name] = Load(name, bus1_name, mw, mvar)

if __name__ == "__main__":

    circuit1 = Circuit("Test Circuit")
    print(circuit1.name)
    print(type(circuit1.name))

    print(circuit1.buses)
    print(type(circuit1.buses))
    print(circuit1.transformers)
    print(circuit1.transmission_lines)
    print(circuit1.generators)
    print(circuit1.loads)

    circuit1.add_bus("Bus 1", 20.0)
    circuit1.add_bus("Bus 2", 230.0)
    print(list(circuit1.buses.keys()))
    print(circuit1.buses["Bus 1"].name, circuit1.buses["Bus 1"].nominal_kv)

    circuit1.add_transformer("T1", "Bus 1", "Bus 2", 0.01, 0.10)
    print(list(circuit1.transformers.keys()))
    print(
        circuit1.transformers["T1"].name,
        circuit1.transformers["T1"].bus1_name,
        circuit1.transformers["T1"].bus2_name,
        circuit1.transformers["T1"].r,
        circuit1.transformers["T1"].x
    )

    circuit1.add_transmission_line("Line 1", "Bus 1", "Bus 2", 0.02, 0.25, 0.0, 0.04)
    print(list(circuit1.transmission_lines.keys()))
    print(
        circuit1.transmission_lines["Line 1"].name,
        circuit1.transmission_lines["Line 1"].bus1_name,
        circuit1.transmission_lines["Line 1"].bus2_name,
        circuit1.transmission_lines["Line 1"].r,
        circuit1.transmission_lines["Line 1"].x,
        circuit1.transmission_lines["Line 1"].g,
        circuit1.transmission_lines["Line 1"].b
    )

    circuit1.add_load("Load 1", "Bus 2", 50.0, 30.0)
    print(list(circuit1.loads.keys()))
    print(
        circuit1.loads["Load 1"].name,
        circuit1.loads["Load 1"].bus1_name,
        circuit1.loads["Load 1"].mw,
        circuit1.loads["Load 1"].mvar
    )

    circuit1.add_generator("G1", "Bus 1", 1.04, 100.0)
    print(list(circuit1.generators.keys()))
    print(
        circuit1.generators["G1"].name,
        circuit1.generators["G1"].bus1_name,
        circuit1.generators["G1"].voltage_setpoint,
        circuit1.generators["G1"].mw_setpoint
    )