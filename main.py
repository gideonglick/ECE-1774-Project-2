from settings import Settings
from circuit import Circuit
from bus import Bus
import numpy as np

if __name__ == "__main__":
    Bus.bus_counter = 0

    circuit1 = Circuit("Angle Test Circuit")
    circuit1.settings = Settings()
    circuit1.settings.circuit = circuit1

    # buses with nonzero angles
    circuit1.buses["Bus 1"] = Bus("Bus 1", 230.0, "Slack", 1.05, 0.0)
    circuit1.buses["Bus 2"] = Bus("Bus 2", 230.0, "PQ", 0.98, -0.08)
    circuit1.buses["Bus 3"] = Bus("Bus 3", 230.0, "PV", 1.02, 0.12)

    # network
    circuit1.add_transmission_line("Line 1", "Bus 1", "Bus 2", 0.02, 0.06, 0.0, 0.03)
    circuit1.add_transmission_line("Line 2", "Bus 2", "Bus 3", 0.08, 0.24, 0.0, 0.025)
    circuit1.add_transformer("T1", "Bus 1", "Bus 3", 0.01, 0.04)

    circuit1.calc_ybus()

    print("Ybus Matrix:")
    print(circuit1.ybus)
    print()

    # just magnitudes
    voltages = np.array([1.05, 0.98, 1.02])

    # test every bus
    for bus_name, bus in circuit1.buses.items():
        Pi, Qi = circuit1.settings.compute_power_injection(bus, circuit1.ybus, voltages)

        print(f"Testing {bus_name}")
        print("Bus index:", bus.bus_index)
        print("Bus type:", bus.bus_type)
        print("Voltage magnitude:", voltages[bus.bus_index])
        print("Delta:", bus.delta)
        print("Pi =", Pi)
        print("Qi =", Qi)
        print()