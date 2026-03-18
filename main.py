from settings import Settings
from circuit import Circuit
from bus import Bus
from generator import Generator
from load import Load

if __name__ == "__main__":
    print("----- TEST 1: Create settings object -----")
    settings1 = Settings()
    print(settings1.freq)
    print(settings1.sbase)

    print("\n----- TEST 2: Create circuit object -----")
    circuit1 = Circuit("Test Circuit")
    print(circuit1.name)

    print("\n----- TEST 3: Create bus objects and store in circuit -----")
    bus1 = Bus("Bus 1", 230.0, "Slack")
    bus2 = Bus("Bus 2", 115.0, "PQ")

    circuit1.buses["Bus 1"] = bus1
    circuit1.buses["Bus 2"] = bus2

    print(list(circuit1.buses.keys()))
    print(circuit1.buses["Bus 1"].name, circuit1.buses["Bus 1"].bus_type, circuit1.buses["Bus 1"].vpu, circuit1.buses["Bus 1"].delta)
    print(circuit1.buses["Bus 2"].name, circuit1.buses["Bus 2"].bus_type, circuit1.buses["Bus 2"].vpu, circuit1.buses["Bus 2"].delta)

    print("\n----- TEST 4: Invalid bus type -----")
    try:
        bad_bus = Bus("Bus 3", 69.0, "Invalid")
    except ValueError as e:
        print(e)

    print("\n----- TEST 5: Create generator object and store in circuit -----")
    gen1 = Generator("G1", "Bus 1", 1.04, 50.0, settings1)
    circuit1.generators["G1"] = gen1

    print(list(circuit1.generators.keys()))
    print(circuit1.generators["G1"].name)
    print(circuit1.generators["G1"].bus1_name)
    print(circuit1.generators["G1"].voltage_setpoint)
    print(circuit1.generators["G1"].mw_setpoint)
    print(circuit1.generators["G1"].p)

    print("\n----- TEST 6: Create load object and store in circuit -----")
    load1 = Load("Load 1", "Bus 2", 50.0, 30.0, settings1)
    circuit1.loads["Load 1"] = load1

    print(list(circuit1.loads.keys()))
    print(circuit1.loads["Load 1"].name)
    print(circuit1.loads["Load 1"].bus1_name)
    print(circuit1.loads["Load 1"].mw)
    print(circuit1.loads["Load 1"].mvar)
    print(circuit1.loads["Load 1"].calc_p())
    print(circuit1.loads["Load 1"].calc_q())