from settings import Settings
from circuit import Circuit
from bus import Bus
from generator import Generator
from load import Load
import numpy as np

if __name__ == "__main__":
    Bus.bus_counter = 0

    circuit1 = Circuit("Mismatch Test")
    circuit1.settings = Settings()
    circuit1.settings.circuit = circuit1

    circuit1.buses["Bus 1"] = Bus("Bus 1", 230.0, "Slack", 1.05, 0.0)
    circuit1.buses["Bus 2"] = Bus("Bus 2", 230.0, "PQ", 0.98, -0.08)
    circuit1.buses["Bus 3"] = Bus("Bus 3", 230.0, "PV", 1.02, 0.12)

    circuit1.add_transmission_line("Line 1", "Bus 1", "Bus 2", 0.02, 0.06, 0.0, 0.03)
    circuit1.add_transmission_line("Line 2", "Bus 2", "Bus 3", 0.08, 0.24, 0.0, 0.025)
    circuit1.add_transformer("T1", "Bus 1", "Bus 3", 0.01, 0.04)

    circuit1.generators["G1"] = Generator("G1", "Bus 3", 1.02, 120.0, circuit1.settings)
    circuit1.loads["L1"] = Load("L1", "Bus 2", 90.0, 30.0, circuit1.settings)

    circuit1.calc_ybus()

    voltages = np.array([1.05, 0.98, 1.02])

    mismatch_vector = circuit1.settings.compute_power_mismatch(circuit1.buses, circuit1.ybus, voltages)

    print("Mismatch vector:")
    print(mismatch_vector)