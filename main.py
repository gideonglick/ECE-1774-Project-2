from settings import Settings
from circuit import Circuit
from bus import Bus
from generator import Generator
from load import Load
from jacobian import Jacobian, JacobianFormat
import numpy as np

if __name__ == "__main__":
    Bus.bus_counter = 0

    # Sbase = 100 MVA
    # Vbase = 15 kV at buses 1, 3 | 345 kV at buses 2, 4, 5

    circuit1 = Circuit("Glover Example 6.9")
    circuit1.settings = Settings()
    circuit1.settings.circuit = circuit1

    # Bus definitions
    circuit1.buses["Bus 1"] = Bus("Bus 1", 15.0,  "Slack", 1.0,  0.0)
    circuit1.buses["Bus 2"] = Bus("Bus 2", 345.0, "PQ",    1.0,  0.0)
    circuit1.buses["Bus 3"] = Bus("Bus 3", 15.0,  "PV",    1.05, 0.0)
    circuit1.buses["Bus 4"] = Bus("Bus 4", 345.0, "PQ",    1.0,  0.0)
    circuit1.buses["Bus 5"] = Bus("Bus 5", 345.0, "PQ",    1.0,  0.0)

    # Transformers
    circuit1.add_transformer("T1", "Bus 1", "Bus 5", 0.00150, 0.02)
    circuit1.add_transformer("T2", "Bus 3", "Bus 4", 0.00075, 0.01)

    # Transmission lines
    circuit1.add_transmission_line("L1", "Bus 2", "Bus 4", 0.0090,  0.100, 0.0, 1.72)
    circuit1.add_transmission_line("L2", "Bus 2", "Bus 5", 0.0045,  0.050, 0.0, 0.88)
    circuit1.add_transmission_line("L3", "Bus 4", "Bus 5", 0.00225, 0.025, 0.0, 0.44)

    # Loads and generators
    circuit1.loads["Load2"] = Load("Load2", "Bus 2", 800.0, 280.0, circuit1.settings)

    circuit1.generators["Gen3"] = Generator("Gen3", "Bus 3", 1.05, 520.0, circuit1.settings)
    circuit1.loads["Load3"] = Load("Load3", "Bus 3", 80.0, 40.0, circuit1.settings)

    # Ybus
    circuit1.calc_ybus()

    print("Ybus:")
    print(circuit1.ybus.round(4))

    # Flat start
    voltages = np.array([bus.vpu for bus in circuit1.buses.values()], dtype=float)
    angles = np.array([bus.delta for bus in circuit1.buses.values()], dtype=float)

    mismatch_table = circuit1.settings.compute_power_mismatch(
        circuit1.buses, circuit1.ybus, voltages, angles
    )

    print("\nMismatch table (flat start):")
    print(mismatch_table.to_string(index=False))

    # Jacobian at flat start
    jac = Jacobian(circuit1)
    J = jac.calc_jacobian(circuit1.buses, circuit1.ybus, angles, voltages)

    print("\nJacobian matrix (flat start):")
    formatter = JacobianFormat(jac)
    formatter.print_dataframe()

    # Dimension check
    expected_mismatch_length = (
        sum(1 for bus in circuit1.buses.values() if bus.bus_type != "Slack")
        + sum(1 for bus in circuit1.buses.values() if bus.bus_type == "PQ")
    )

    print("\nExpected mismatch length:", expected_mismatch_length)
    print("Jacobian shape:", J.shape)

    assert J.shape[0] == expected_mismatch_length, "Dimension mismatch!"
    assert J.shape[1] == expected_mismatch_length, "Dimension mismatch!"
    print("Dimensions match ✓")

    # PowerWorld converged solution
    converged_voltages = np.array([1.00000, 0.83377, 1.05000, 1.01930, 0.97429], dtype=float)
    converged_angles = np.array([0.00, -22.41, -0.60, -2.83, -4.55], dtype=float)  # degrees

    converged_mismatch_table = circuit1.settings.compute_power_mismatch(
        circuit1.buses, circuit1.ybus, converged_voltages, converged_angles
    )

    print("\nMismatch table at converged solution:")
    print(converged_mismatch_table.to_string(index=False))

    J_converged = jac.calc_jacobian(
        circuit1.buses, circuit1.ybus, converged_angles, converged_voltages
    )

    print("\nJacobian at converged solution:")
    formatter.print_dataframe()