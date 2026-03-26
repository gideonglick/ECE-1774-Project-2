import numpy as np

class Settings:
    def __init__(self, freq: float = 60, sbase: float = 100):
        self.freq = freq
        self.sbase = sbase

    def compute_power_injection(self, bus, ybus, voltages):
        i = bus.bus_index

        Vi = voltages[i]
        delta_i = bus.delta

        Pi = 0.0
        Qi = 0.0

        for j in range(len(voltages)):
            Vj = voltages[j]

            delta_j = 0.0
            for other_bus in self.circuit.buses.values():
                if other_bus.bus_index == j:
                    delta_j = other_bus.delta
                    break

            Gij = ybus.iloc[i, j].real
            Bij = ybus.iloc[i, j].imag
            delta_ij = delta_i - delta_j

            Pi += Vi * Vj * (Gij * np.cos(delta_ij) + Bij * np.sin(delta_ij))
            Qi += Vi * Vj * (Gij * np.sin(delta_ij) - Bij * np.cos(delta_ij))

        return Pi, Qi