from settings import Settings
from circuit import Circuit
from bus import Bus
from generator import Generator
from load import Load
from solver import Solver


if __name__ == "__main__":
    Bus.bus_counter = 0

    # Test System: 5-Bus System
    circuit1 = Circuit("Glover Example 6.9")
    circuit1.settings = Settings()
    circuit1.settings.circuit = circuit1

    # Turn on ZIP load modeling
    circuit1.settings.use_zip = True

    # Bus definitions
    circuit1.buses["Bus 1"] = Bus("Bus 1", 15.0, "Slack", 1.0, 0.0)
    circuit1.buses["Bus 2"] = Bus("Bus 2", 345.0, "PQ", 1.0, 0.0)
    circuit1.buses["Bus 3"] = Bus("Bus 3", 15.0, "PV", 1.05, 0.0)
    circuit1.buses["Bus 4"] = Bus("Bus 4", 345.0, "PQ", 1.0, 0.0)
    circuit1.buses["Bus 5"] = Bus("Bus 5", 345.0, "PQ", 1.0, 0.0)

    # Transformers
    circuit1.add_transformer("T1", "Bus 1", "Bus 5", 0.00150, 0.02)
    circuit1.add_transformer("T2", "Bus 3", "Bus 4", 0.00075, 0.01)

    # Transmission lines
    circuit1.add_transmission_line("L1", "Bus 2", "Bus 4", 0.0090, 0.100, 0.0, 1.72)
    circuit1.add_transmission_line("L2", "Bus 2", "Bus 5", 0.0045, 0.050, 0.0, 0.88)
    circuit1.add_transmission_line("L3", "Bus 4", "Bus 5", 0.00225, 0.025, 0.0, 0.44)

    # Loads and generators
    circuit1.loads["Load2"] = Load(
        "Load2", "Bus 2", 900.0, 420.0, circuit1.settings,
        zp=0.2, ip=0.3, pp=0.5,
        zq=0.2, iq=0.3, pq=0.5
    )

    circuit1.generators["Gen1"] = Generator(
        "Gen1", "Bus 1", 1.0, 0.0, circuit1.settings, xd_subtransient=0.0
    )

    circuit1.generators["Gen3"] = Generator(
        "Gen3", "Bus 3", 1.05, 520.0, circuit1.settings, xd_subtransient=0.0
    )

    circuit1.loads["Load3"] = Load(
        "Load3", "Bus 3", 80.0, 40.0, circuit1.settings,
        zp=0.2, ip=0.3, pp=0.5,
        zq=0.2, iq=0.3, pq=0.5
    )

    solver = Solver(circuit1)
    solver.run(force_print=True)