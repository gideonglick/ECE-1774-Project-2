import pandas as pd
import numpy as np


class Settings:
    def __init__(self, circuit=None, freq: float = 60, sbase: float = 100):
        self.circuit = circuit
        self.freq = freq
        self.sbase = sbase
        self.use_zip = False

    def compute_power_injection(self, bus, ybus, voltages, angles):
        i = bus.bus_index
        Vi = voltages[i]
        delta_i = np.deg2rad(angles[i])
        Pi = Qi = 0.0
        for j in range(len(voltages)):
            Vj = voltages[j]
            delta_j = np.deg2rad(angles[j])
            Gij = ybus.iloc[i, j].real
            Bij = ybus.iloc[i, j].imag
            d = delta_i - delta_j
            Pi += Vi * Vj * (Gij * np.cos(d) + Bij * np.sin(d))
            Qi += Vi * Vj * (Gij * np.sin(d) - Bij * np.cos(d))
        return Pi, Qi

    def compute_power_mismatch(self, buses, ybus, voltages, angles):
        p_mis, q_mis = [], []
        for bus in buses.values():
            if bus.bus_type == "Slack":
                continue

            P_calc, Q_calc = self.compute_power_injection(bus, ybus, voltages, angles)
            P_spec = Q_spec = 0.0

            for gen in self.circuit.generators.values():
                if gen.bus1_name == bus.name:
                    P_spec += gen.p

            for load in self.circuit.loads.values():
                if load.bus1_name == bus.name:
                    i = bus.bus_index
                    P_spec -= load.calc_p(voltages[i])
                    Q_spec -= load.calc_q(voltages[i])

            p_mis.append(P_spec - P_calc)

            if bus.bus_type == "PQ":
                q_mis.append(Q_spec - Q_calc)

        return np.array(p_mis + q_mis, dtype=float)

    def compute_mismatch_table(self, buses, ybus, voltages, angles):
        rows = []
        for bus in buses.values():
            P_calc, Q_calc = self.compute_power_injection(bus, ybus, voltages, angles)
            P_spec = Q_spec = 0.0

            for gen in self.circuit.generators.values():
                if gen.bus1_name == bus.name:
                    P_spec += gen.p

            for load in self.circuit.loads.values():
                if load.bus1_name == bus.name:
                    i = bus.bus_index
                    P_spec -= load.calc_p(voltages[i])
                    Q_spec -= load.calc_q(voltages[i])

            if bus.bus_type == "Slack":
                P_mismatch = Q_mismatch = 0.0
            elif bus.bus_type == "PV":
                P_mismatch = (P_spec - P_calc) * self.sbase
                Q_mismatch = 0.0
            else:
                P_mismatch = (P_spec - P_calc) * self.sbase
                Q_mismatch = (Q_spec - Q_calc) * self.sbase

            S_mismatch = np.sqrt(P_mismatch ** 2 + Q_mismatch ** 2)

            rows.append({
                "Number": bus.bus_index + 1,
                "Name": bus.name,
                "Area Name": 1,
                "Type": bus.bus_type,
                "Mismatch MW": round(P_mismatch, 2),
                "Mismatch Mvar": round(Q_mismatch, 2),
                "Mismatch MVA": round(S_mismatch, 2)
            })

        return pd.DataFrame(rows)