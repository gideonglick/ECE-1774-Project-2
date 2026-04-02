from settings import Settings
from circuit import Circuit
from bus import Bus
from generator import Generator
from load import Load
from jacobian import Jacobian, JacobianFormat
from powerflow import PowerFlow
import numpy as np

if __name__ == "__main__":
    Bus.bus_counter = 0

    # Test System: 5-Bus System
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

    # Build Ybus
    circuit1.calc_ybus()

    print("Ybus:")
    print(circuit1.ybus.round(4))

    # Flat Start Validation
    flat_voltages = np.array([bus.vpu for bus in circuit1.buses.values()], dtype=float)
    flat_angles = np.array([bus.delta for bus in circuit1.buses.values()], dtype=float)

    mismatch_vector = circuit1.settings.compute_power_mismatch(
        circuit1.buses, circuit1.ybus, flat_voltages, flat_angles
    )

    mismatch_table = circuit1.settings.compute_mismatch_table(
        circuit1.buses, circuit1.ybus, flat_voltages, flat_angles
    )

    print("\nMismatch vector (flat start):")
    print(mismatch_vector)

    print("\nMismatch table (flat start):")
    print(mismatch_table.to_string(index=False))

    # Jacobian Verification
    jac = Jacobian(circuit1)
    J = jac.calc_jacobian(circuit1.buses, circuit1.ybus, flat_angles, flat_voltages)

    print("\nJacobian matrix (flat start):")
    formatter = JacobianFormat(jac)
    formatter.print_dataframe()

    print("\nMismatch vector length:", len(mismatch_vector))
    print("Jacobian shape:", J.shape)

    assert J.shape[0] == len(mismatch_vector), "Dimension mismatch!"
    assert J.shape[1] == len(mismatch_vector), "Dimension mismatch!"
    print("Jacobian dimensions match mismatch vector ✓")

    # Newton-Raphson Solve
    pf = PowerFlow(circuit1)
    solved_voltages, solved_angles, converged, iterations = pf.solve(
        circuit1.buses,
        circuit1.ybus,
        tol=0.001,
        max_iter=50
    )

    print("\nNewton-Raphson Results:")
    for bus in circuit1.buses.values():
        print(f"{bus.name}: V = {bus.vpu:.5f} pu, angle = {bus.delta:.5f} deg")

    print("\nConverged:", converged)
    print("Iterations:", iterations)
    print("Final mismatch vector:")
    print(pf.final_mismatch)

    mismatch_norm = np.max(np.abs(pf.final_mismatch))
    print("Final mismatch norm:", mismatch_norm)

    if mismatch_norm < 0.001:
        print("Mismatch norm converged below tolerance ✓")
    else:
        print("Mismatch norm did not converge below tolerance")

    solved_mismatch_table = circuit1.settings.compute_mismatch_table(
        circuit1.buses, circuit1.ybus, solved_voltages, solved_angles
    )

    print("\nMismatch table at Newton-Raphson solution:")
    print(solved_mismatch_table.to_string(index=False))