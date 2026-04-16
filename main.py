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

    circuit1 = Circuit("Glover Example 6.9")
    circuit1.settings = Settings(circuit=circuit1)

    circuit1.buses["Bus 1"] = Bus("Bus 1", 15.0,  "Slack", 1.0,  0.0)
    circuit1.buses["Bus 2"] = Bus("Bus 2", 345.0, "PQ",    1.0,  0.0)
    circuit1.buses["Bus 3"] = Bus("Bus 3", 15.0,  "PV",    1.05, 0.0)
    circuit1.buses["Bus 4"] = Bus("Bus 4", 345.0, "PQ",    1.0,  0.0)
    circuit1.buses["Bus 5"] = Bus("Bus 5", 345.0, "PQ",    1.0,  0.0)

    circuit1.add_transformer("T1", "Bus 1", "Bus 5", 0.00150, 0.02)
    circuit1.add_transformer("T2", "Bus 3", "Bus 4", 0.00075, 0.01)

    circuit1.add_transmission_line("L1", "Bus 2", "Bus 4", 0.0090,  0.100, 0.0, 1.72)
    circuit1.add_transmission_line("L2", "Bus 2", "Bus 5", 0.0045,  0.050, 0.0, 0.88)
    circuit1.add_transmission_line("L3", "Bus 4", "Bus 5", 0.00225, 0.025, 0.0, 0.44)

    circuit1.loads["Load2"] = Load("Load2", "Bus 2", 800.0, 280.0, circuit1.settings)
    circuit1.generators["Gen3"] = Generator("Gen3", "Bus 3", 1.05, 520.0, circuit1.settings, xd_subtransient=0.0)
    circuit1.generators["Gen1"] = Generator("Gen1", "Bus 1", 1.0,  0.0,   circuit1.settings, xd_subtransient=0.0)
    circuit1.loads["Load3"] = Load("Load3", "Bus 3", 80.0, 40.0, circuit1.settings)

    circuit1.calc_ybus()

    print("Ybus:")
    print(circuit1.ybus.round(4))

    # -------------------------------------------------------------------------
    # MODE 1: Power Flow
    # -------------------------------------------------------------------------
    print("\n" + "="*60)
    print("MODE 1: POWER FLOW")
    print("="*60)

    flat_voltages = np.array([bus.vpu for bus in circuit1.buses.values()], dtype=float)
    flat_angles   = np.array([bus.delta for bus in circuit1.buses.values()], dtype=float)

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

    pf = PowerFlow(circuit1)
    solved_voltages, solved_angles, converged, iterations = pf.solve(
        tol=0.001,
        max_iter=50
    )

    print("\nNewton-Raphson Results:")
    for bus in circuit1.buses.values():
        print(f"  {bus.name}: V = {bus.vpu:.5f} pu, angle = {bus.delta:.5f} deg")

    print(f"\nConverged: {converged}")
    print(f"Iterations: {iterations}")

    mismatch_norm = np.max(np.abs(pf.final_mismatch))
    print(f"Final mismatch norm: {mismatch_norm}")
    if mismatch_norm < 0.001:
        print("Mismatch norm converged below tolerance ✓")
    else:
        print("Mismatch norm did NOT converge below tolerance ✗")

    solved_mismatch_table = circuit1.settings.compute_mismatch_table(
        circuit1.buses, circuit1.ybus, solved_voltages, solved_angles
    )
    print("\nMismatch table at Newton-Raphson solution:")
    print(solved_mismatch_table.to_string(index=False))

    # -------------------------------------------------------------------------
    # MODE 2: Fault Study
    # -------------------------------------------------------------------------
    print("\n" + "="*60)
    print("MODE 2: FAULT STUDY")
    print("="*60)

    # Set subtransient reactances for fault study
    circuit1.generators["Gen1"].xd_subtransient = 0.20
    circuit1.generators["Gen3"].xd_subtransient = 0.20

    # Confirm xd values are set
    print("\nGenerator xd check:")
    for name, gen in circuit1.generators.items():
        print(f"  {name}: xd = {gen.xd_subtransient}")

    # Confirm faulted Ybus diagonal is correct
    ybus_f = pf.calc_ybus_faulted()
    print("\nYbus diagonal comparison (normal vs faulted):")
    for name in circuit1.buses.keys():
        print(f"  {name}: normal={circuit1.ybus.loc[name, name]:.4f}  faulted={ybus_f.loc[name, name]:.4f}")

    fault_bus = "Bus 3"
    print(f"\nFault location  : {fault_bus}")
    print(f"Prefault voltage: {circuit1.buses[fault_bus].vpu:.4f} pu")

    results = pf.solve_fault(fault_bus_name=fault_bus)

    print("\nPost-Fault Bus Voltage Summary:")
    print(results.to_string(index=False))

    # -------------------------------------------------------------------------
    # Validation Checks
    # -------------------------------------------------------------------------
    print("\n" + "="*60)
    print("VALIDATION CHECKS")
    print("="*60)

    faulted_voltage = abs(pf.bus_voltages[fault_bus])
    print(f"\nCheck 1 - Faulted bus voltage is 0 pu:")
    print(f"  {fault_bus} voltage = {faulted_voltage:.6f} pu", end="  ")
    print("✓" if faulted_voltage < 1e-6 else "✗ (expected ~0)")

    prefault_voltage = circuit1.buses[fault_bus].vpu
    print(f"\nCheck 2 - All other bus voltages between 0 and {prefault_voltage:.4f} pu:")
    for bus_name, V in pf.bus_voltages.items():
        if bus_name == fault_bus:
            continue
        v_mag = abs(V)
        ok = 0 < v_mag < prefault_voltage
        print(f"  {bus_name} voltage = {v_mag:.4f} pu", end="  ")
        print("✓" if ok else "✗")

    If_mag = abs(pf.fault_current)
    print(f"\nCheck 3 - Fault current is nonzero:")
    print(f"  |If| = {If_mag:.4f} pu", end="  ")
    print("✓" if If_mag > 0 else "✗")

    print("\nFault study validation complete.")