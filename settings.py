import numpy as np


class Settings:
    def __init__(self, freq: float = 60, sbase: float = 100):
        self.freq = freq
        self.sbase = sbase

    def compute_power_injection(self, bus, ybus, voltages, angles=None):
        i  = bus.bus_index
        Vi = voltages[i]

        # Use passed angles array if provided, otherwise fall back to bus.delta (degrees -> radians)
        if angles is not None:
            delta_i = angles[i]
        else:
            delta_i = np.deg2rad(bus.delta)

        Pi = 0.0
        Qi = 0.0

        for j in range(len(voltages)):
            Vj = voltages[j]

            if angles is not None:
                delta_j = angles[j]
            else:
                delta_j = 0.0
                for other_bus in self.circuit.buses.values():
                    if other_bus.bus_index == j:
                        delta_j = np.deg2rad(other_bus.delta)
                        break

            Gij = ybus.iloc[i, j].real
            Bij = ybus.iloc[i, j].imag
            delta_ij = delta_i - delta_j

            Pi += Vi * Vj * (Gij * np.cos(delta_ij) + Bij * np.sin(delta_ij))
            Qi += Vi * Vj * (Gij * np.sin(delta_ij) - Bij * np.cos(delta_ij))

        return Pi, Qi

    def compute_power_mismatch(self, buses, ybus, voltages):
        mismatch_vector = []

        for bus in buses.values():
            if bus.bus_type == "Slack":
                continue

            P_calc, Q_calc = self.compute_power_injection(bus, ybus, voltages)

            P_spec = 0.0
            Q_spec = 0.0

            for generator in self.circuit.generators.values():
                if generator.bus1_name == bus.name:
                    P_spec += generator.p

            for load in self.circuit.loads.values():
                if load.bus1_name == bus.name:
                    P_spec -= load.calc_p()
                    Q_spec -= load.calc_q()

            real_power_mismatch = P_spec - P_calc

            if bus.bus_type == "PQ":
                reactive_power_mismatch = Q_spec - Q_calc
                mismatch_vector += [real_power_mismatch, reactive_power_mismatch]
            else:
                mismatch_vector += [real_power_mismatch]

        return np.array(mismatch_vector)