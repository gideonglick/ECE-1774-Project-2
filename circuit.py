from typing import Dict, List, Optional
from bus import Bus
from load import Load
from generator import Generator
from transformer import Transformer
from transmissionLine import TransmissionLine
from shuntCompensator import ShuntCompensator
from settings import Settings
import numpy as np
import pandas as pd


class Circuit:
    def __init__(self, name: str, s_base: float = 100.0, freq: float = 60.0):
        self.name = name
        self.s_base = s_base  # system MVA base
        # Settings is shared by Circuit, Generators, Loads, and PowerFlow
        self.settings = Settings(circuit=self, freq=freq, sbase=s_base)

        self.buses: Dict[str, Bus] = {}
        self.loads: Dict[str, Load] = {}
        self.generators: Dict[str, Generator] = {}
        self.transmission_lines: Dict[str, TransmissionLine] = {}
        self.transformers: Dict[str, Transformer] = {}
        self.shunt_compensators: Dict[str, ShuntCompensator] = {}

    def add_bus(self, name: str, nominal_kv: float, bus_type: str,
                vpu: float = 1.0, delta: float = 0.0):
        if name in self.buses:
            raise ValueError(f"bus {name} already exists")
        self.buses[name] = Bus(name, nominal_kv, bus_type, vpu, delta)

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

    def add_transmission_line(self, name: str, bus1_name: str, bus2_name: str,
                              r: float, x: float, g: float, b: float):
        if name in self.transmission_lines:
            raise ValueError(f"transmission_line {name} already exists")
        if bus1_name not in self.buses.keys():
            raise ValueError(f"bus {bus1_name} does not exist")
        if bus2_name not in self.buses.keys():
            raise ValueError(f"bus {bus2_name} does not exist")
        if bus1_name == bus2_name:
            raise ValueError("transmission line cannot connect a bus to itself")
        self.transmission_lines[name] = TransmissionLine(name, bus1_name, bus2_name, r, x, g, b)

    def add_generator(self, name: str, bus1_name: str, voltage_setpoint: float,
                      mw_setpoint: float, xd_subtransient: float = 0.0):
        if name in self.generators:
            raise ValueError(f"generator {name} already exists")
        if bus1_name not in self.buses.keys():
            raise ValueError(f"bus {bus1_name} does not exist")
        self.generators[name] = Generator(
            name, bus1_name, voltage_setpoint, mw_setpoint,
            self.settings, xd_subtransient
        )

    def add_load(self, name: str, bus1_name: str, mw: float, mvar: float):
        if name in self.loads:
            raise ValueError(f"load {name} already exists")
        if bus1_name not in self.buses.keys():
            raise ValueError(f"bus {bus1_name} does not exist")
        self.loads[name] = Load(name, bus1_name, mw, mvar, self.settings)

    def add_shunt_compensator(self, name: str, bus1_name: str, mvar_rating: float):
        """
        Add a shunt capacitor (mvar_rating > 0) or reactor (mvar_rating < 0).
        mvar_rating is in actual MVAR; conversion to per-unit uses self.s_base.
        """
        if name in self.shunt_compensators:
            raise ValueError(f"shunt compensator {name} already exists")
        if bus1_name not in self.buses.keys():
            raise ValueError(f"bus {bus1_name} does not exist")
        if mvar_rating == 0:
            raise ValueError("shunt compensator MVAR rating cannot be zero")
        self.shunt_compensators[name] = ShuntCompensator(
            name, bus1_name, mvar_rating, s_base=self.s_base
        )

    def calc_ybus(self):
        bus_names = list(self.buses.keys())
        N = len(bus_names)
        bus_index = {name: i for i, name in enumerate(bus_names)}
        ybus_matrix = np.zeros((N, N), dtype=complex)

        # Stamp transformers
        for transformer in self.transformers.values():
            yprim = transformer.calc_yprim()
            i = bus_index[transformer.bus1_name]
            j = bus_index[transformer.bus2_name]
            ybus_matrix[i, i] += yprim.iloc[0, 0]
            ybus_matrix[i, j] += yprim.iloc[0, 1]
            ybus_matrix[j, i] += yprim.iloc[1, 0]
            ybus_matrix[j, j] += yprim.iloc[1, 1]

        # Stamp transmission lines
        for line in self.transmission_lines.values():
            yprim = line.calc_yprim()
            i = bus_index[line.bus1_name]
            j = bus_index[line.bus2_name]
            ybus_matrix[i, i] += yprim.iloc[0, 0]
            ybus_matrix[i, j] += yprim.iloc[0, 1]
            ybus_matrix[j, i] += yprim.iloc[1, 0]
            ybus_matrix[j, j] += yprim.iloc[1, 1]

        # Stamp shunt compensators (diagonal only)
        for comp in self.shunt_compensators.values():
            yprim = comp.calc_yprim()
            i = bus_index[comp.bus1_name]
            ybus_matrix[i, i] += yprim.iloc[0, 0]

        self.ybus = pd.DataFrame(
            ybus_matrix,
            index=bus_names,
            columns=bus_names
        )