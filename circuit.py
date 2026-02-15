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
        try:
            bus = self.buses[bus1_name]
        except KeyError as e:
            raise ValueError(f"bus {e.args[0]} does not exist")
        try:
            bus2 = self.buses[bus2_name]
        except KeyError:
            raise ValueError(f"bus {bus2_name} does not exist")
        if bus1_name == bus2_name:
            raise ValueError("transformer cannot connect a bus to itself")

        self.transformers[name] = Transformer(name, bus1_name, bus2_name, r, x)

    def add_transmission_line(self, name:str, bus1_name:str, bus2_name:str, r:float, x:float, g:float, b:float):
        if name in self.transmission_lines:
            raise ValueError(f"transmission_line {name} already exists")
        try:
            bus = self.buses[bus1_name]
        except KeyError as e:
            raise ValueError(f"bus {e.args[0]} does not exist")
        try:
            bus2 = self.buses[bus2_name]
        except KeyError:
            raise ValueError(f"bus {bus2_name} does not exist")
        if bus1_name == bus2_name:
            raise ValueError("transmission line cannot connect a bus to itself")

        self.transmission_lines[name] = TransmissionLine(name, bus1_name, bus2_name, r, x, g, b)

    def add_generator(self, name: str, bus1_name, voltage_setpoint:float, mw_setpoint: float):
        if name in self.generators:
            raise ValueError(f"generator {name} already exists")
        try:
            bus = self.buses[bus1_name]
        except KeyError as e:
            raise ValueError(f"bus {e.args[0]} does not exist")

        self.generators[name] = Generator(name, bus1_name, voltage_setpoint, mw_setpoint)

    def add_load(self, name: str, bus1_name: str, mw:float, mvar:float):
        if name in self.loads:
            raise ValueError(f"load {name} already exists")
        try:
            bus = self.buses[bus1_name]
        except KeyError as e:
            raise ValueError(f"bus {e.args[0]} does not exist")

        self.loads[name] = Load(name, bus1_name, mw, mvar)

