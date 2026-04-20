from settings import Settings
from circuit import Circuit
from bus import Bus
from generator import Generator
from load import Load
from solver import Solver


# =============================================================
#  CASE 1 -- Module 16 simple 2-bus validation
#  G -- T1 -- line -- T2 -- M, everything lumped into one line
#
#  Expected fault currents (Vf = 1.0 pu):
#    Fault at Bus 1: |If| = 8.647 pu
#    Fault at Bus 2: |If| = 7.198 pu
# =============================================================
def run_module_16_simple():
    Bus.bus_counter = 0

    circuit = Circuit("Module 16 -- 2-Bus Simple Case")
    circuit.settings = Settings()
    circuit.settings.circuit = circuit

    circuit.buses["Bus 1"] = Bus("Bus 1", 13.8, "Slack", 1.0, 0.0)
    circuit.buses["Bus 2"] = Bus("Bus 2", 13.8, "PV",    1.0, 0.0)

    # T1 + line + T2 lumped: X = 0.10 + 0.105 + 0.10 = 0.305 pu
    circuit.add_transmission_line(
        "T1+Line+T2", "Bus 1", "Bus 2",
        r=0.0, x=0.305, g=0.0, b=0.0
    )

    circuit.generators["Gen"] = Generator(
        "Gen", "Bus 1", 1.0, 0.0, circuit.settings, xd_subtransient=0.15
    )
    # Motor modeled as generator -- it feeds fault current like a gen
    circuit.generators["Motor"] = Generator(
        "Motor", "Bus 2", 1.0, 0.0, circuit.settings, xd_subtransient=0.20
    )

    solver = Solver(circuit)
    solver.run(
        run_fault=True,
        fault_all_buses=True,
        prefault_voltage=1.0 + 0j,
        skip_power_flow=True,
    )


# =============================================================
#  CASE 2 -- Glover Example 6.9 (5-bus system)
#  Power flow + fault study at every bus, realistic network data
# =============================================================
def run_glover_6_9():
    Bus.bus_counter = 0

    circuit = Circuit("Glover Example 6.9")
    circuit.settings = Settings()
    circuit.settings.circuit = circuit

    circuit.buses["Bus 1"] = Bus("Bus 1", 15.0,  "Slack", 1.0,  0.0)
    circuit.buses["Bus 2"] = Bus("Bus 2", 345.0, "PQ",    1.0,  0.0)
    circuit.buses["Bus 3"] = Bus("Bus 3", 15.0,  "PV",    1.05, 0.0)
    circuit.buses["Bus 4"] = Bus("Bus 4", 345.0, "PQ",    1.0,  0.0)
    circuit.buses["Bus 5"] = Bus("Bus 5", 345.0, "PQ",    1.0,  0.0)

    circuit.add_transformer("T1", "Bus 1", "Bus 5", 0.00150, 0.02)
    circuit.add_transformer("T2", "Bus 3", "Bus 4", 0.00075, 0.01)

    circuit.add_transmission_line("L1", "Bus 2", "Bus 4", 0.0090,  0.100, 0.0, 1.72)
    circuit.add_transmission_line("L2", "Bus 2", "Bus 5", 0.0045,  0.050, 0.0, 0.88)
    circuit.add_transmission_line("L3", "Bus 4", "Bus 5", 0.00225, 0.025, 0.0, 0.44)

    circuit.loads["Load2"] = Load("Load2", "Bus 2", 800.0, 280.0, circuit.settings)
    circuit.loads["Load3"] = Load("Load3", "Bus 3",  80.0,  40.0, circuit.settings)

    circuit.generators["Gen1"] = Generator(
        "Gen1", "Bus 1", 1.0,  0.0,   circuit.settings, xd_subtransient=0.045
    )
    circuit.generators["Gen3"] = Generator(
        "Gen3", "Bus 3", 1.05, 520.0, circuit.settings, xd_subtransient=0.0225
    )

    solver = Solver(circuit)
    solver.run(run_fault=True, fault_all_buses=True)


# =============================================================
#  CASE 3 -- Glover Example 8.5 (textbook validation)
#  Same topology as 6.9 but with simplified fault-study data
#  (Tables 8.3/8.4/8.5): R = 0 everywhere, no line charging,
#  no loads, flat 1.05 pu prefault.
#
#  Should match Glover Table 8.7 to 4 decimal places.
# =============================================================
def run_glover_8_5():
    Bus.bus_counter = 0

    circuit = Circuit("Glover Example 8.5 -- textbook validation")
    circuit.settings = Settings()
    circuit.settings.circuit = circuit

    circuit.buses["Bus 1"] = Bus("Bus 1", 15.0,  "Slack", 1.05, 0.0)
    circuit.buses["Bus 2"] = Bus("Bus 2", 345.0, "PQ",    1.05, 0.0)
    circuit.buses["Bus 3"] = Bus("Bus 3", 15.0,  "PV",    1.05, 0.0)
    circuit.buses["Bus 4"] = Bus("Bus 4", 345.0, "PQ",    1.05, 0.0)
    circuit.buses["Bus 5"] = Bus("Bus 5", 345.0, "PQ",    1.05, 0.0)

    # Transformers -- Table 8.5: R = 0
    circuit.add_transformer("T1", "Bus 1", "Bus 5", 0.0, 0.02)
    circuit.add_transformer("T2", "Bus 3", "Bus 4", 0.0, 0.01)

    # Transmission lines -- Table 8.4: R = 0, B = 0
    circuit.add_transmission_line("L1", "Bus 2", "Bus 4", 0.0, 0.10,  0.0, 0.0)
    circuit.add_transmission_line("L2", "Bus 2", "Bus 5", 0.0, 0.05,  0.0, 0.0)
    circuit.add_transmission_line("L3", "Bus 4", "Bus 5", 0.0, 0.025, 0.0, 0.0)

    # Generators -- Table 8.3
    circuit.generators["Gen1"] = Generator(
        "Gen1", "Bus 1", 1.05, 0.0, circuit.settings, xd_subtransient=0.045
    )
    circuit.generators["Gen3"] = Generator(
        "Gen3", "Bus 3", 1.05, 0.0, circuit.settings, xd_subtransient=0.0225
    )
    # No loads -- unloaded initial condition

    solver = Solver(circuit)
    solver.run(
        run_fault=True,
        fault_all_buses=True,
        prefault_voltage=1.05 + 0j,
        skip_power_flow=True,
    )


# =============================================================
#  Comment out any case you don't want to run
# =============================================================
if __name__ == "__main__":
    run_module_16_simple()
    run_glover_6_9()
    run_glover_8_5()