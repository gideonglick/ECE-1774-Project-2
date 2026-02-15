from circuit import Circuit

def main():

## circuit class test
    circuit1 = Circuit("Test Circuit")

    print(circuit1.name)
    print(type(circuit1.name))

    print(circuit1.buses)
    print(type(circuit1.buses))

    print(circuit1.transformers)
    print(circuit1.transmission_lines)
    print(circuit1.generators)
    print(circuit1.loads)

## add bus test
    circuit1.add_bus("Bus 1", 20.0)
    circuit1.add_bus("Bus 2", 230.0)

    print(list(circuit1.buses.keys()))
    print(circuit1.buses["Bus 1"].name, circuit1.buses["Bus 1"].nominal_kv)

## add transformer test
    circuit1.add_transformer("T1", "Bus 1", "Bus 2", 0.01, 0.10)

    print(list(circuit1.transformers.keys()))

    print(
        circuit1.transformers["T1"].name,
        circuit1.transformers["T1"].bus1_name,
        circuit1.transformers["T1"].bus2_name,
        circuit1.transformers["T1"].r,
        circuit1.transformers["T1"].x
    )

## add transmission_line test
    circuit1.add_transmission_line(
        "Line 1", "Bus 1", "Bus 2",0.02, 0.25, 0.0, 0.04
    )

    print(list(circuit1.transmission_lines.keys()))

    print(
        circuit1.transmission_lines["Line 1"].name,
        circuit1.transmission_lines["Line 1"].bus1_name,
        circuit1.transmission_lines["Line 1"].bus2_name,
        circuit1.transmission_lines["Line 1"].r,
        circuit1.transmission_lines["Line 1"].x,
        circuit1.transmission_lines["Line 1"].g,
        circuit1.transmission_lines["Line 1"].b
    )

#add load test
    circuit1.add_load("Load 1", "Bus 2", 50.0, 30.0)

    print(list(circuit1.loads.keys()))

    print(
        circuit1.loads["Load 1"].name,
        circuit1.loads["Load 1"].bus1_name,
        circuit1.loads["Load 1"].mw,
        circuit1.loads["Load 1"].mvar
    )

#add generator test
    circuit1.add_generator("G1", "Bus 1", 1.04, 100.0)

    print(list(circuit1.generators.keys()))

    print(
        circuit1.generators["G1"].name,
        circuit1.generators["G1"].bus1_name,
        circuit1.generators["G1"].voltage_setpoint,
        circuit1.generators["G1"].mw_setpoint
    )


if __name__ == "__main__":
    main()
