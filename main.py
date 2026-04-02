from settings import Settings
from circuit import Circuit
from bus import Bus
from generator import Generator
from load import Load
import numpy as np

if __name__ == "__main__":
    Bus.bus_counter = 0

    circuit1 = Circuit("PowerWorld 5-Bus")
    circuit1.settings = Settings(freq=60, sbase=100)
    circuit1.settings.circuit = circuit1

    circuit1.buses["One"] = Bus("One", 15.0, "Slack", 1.00000, 0.00)
    circuit1.buses["Two"] = Bus("Two", 345.0, "PQ", 0.83377, -22.41)
    circuit1.buses["Three"] = Bus("Three", 15.0, "PV", 1.05000, -0.60)
    circuit1.buses["Four"] = Bus("Four", 345.0, "PQ", 1.01930, -2.83)
    circuit1.buses["Five"] = Bus("Five", 345.0, "PQ", 0.97429, -4.55)

    circuit1.generators["G1"] = Generator("G1", "One", 1.00000, 394.84, circuit1.settings)
    circuit1.generators["G2"] = Generator("G2", "Three", 1.05000, 520.00, circuit1.settings)

    circuit1.loads["L1"] = Load("L1", "Two", 800.00, 280.00, circuit1.settings)
    circuit1.loads["L2"] = Load("L2", "Three", 80.00, 40.00, circuit1.settings)

    circuit1.add_transformer("T1", "One", "Five", 0.00150, 0.02000)
    circuit1.add_transmission_line("Line 1", "Four", "Two", 0.00900, 0.10000, 0.0, 1.72000)
    circuit1.add_transmission_line("Line 2", "Five", "Two", 0.00450, 0.05000, 0.0, 0.88000)
    circuit1.add_transformer("T2", "Three", "Four", 0.00075, 0.01000)
    circuit1.add_transmission_line("Line 3", "Five", "Four", 0.00225, 0.02500, 0.0, 0.44000)

    circuit1.calc_ybus()

    voltages = np.array([1.0, 1.0, 1.05, 1.0, 1.0], dtype=float)
    angles = np.array([0.0, 0.0, 0.0, 0.0, 0.0], dtype=float)

    mismatch_table = circuit1.settings.compute_power_mismatch(circuit1.buses,circuit1.ybus,voltages,angles)

    print("Ybus:")
    print(circuit1.ybus)
    print()

    print("Mismatch table:")
    print(mismatch_table.to_string(index=False))