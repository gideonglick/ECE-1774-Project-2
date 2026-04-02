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

    # Transmission lines (
    circuit1.add_transmission_line("L1", "Bus 2", "Bus 4", 0.0090,  0.100, 0.0, 1.72)
    circuit1.add_transmission_line("L2", "Bus 2", "Bus 5", 0.0045,  0.050, 0.0, 0.88)
    circuit1.add_transmission_line("L3", "Bus 4", "Bus 5", 0.00225, 0.025, 0.0, 0.44)

    # Bus 2: load only — 800 MW, 280 Mvar
    circuit1.loads["Load2"] = Load("Load2", "Bus 2", 800.0, 280.0, circuit1.settings)

    # Bus 3: PG = 520 MW, PL = 80 MW, QL = 40 Mvar → net P = 4.4 pu
    circuit1.generators["Gen3"] = Generator("Gen3", "Bus 3", 1.05, 520.0, circuit1.settings)
    circuit1.loads["Load3"]     = Load("Load3",     "Bus 3",  80.0,  40.0, circuit1.settings)

    # Ybus
    circuit1.calc_ybus()

    print("Ybus:")
    print(circuit1.ybus.round(4))

    #  Mismatch Vector (flat start)
    voltages = np.array([bus.vpu   for bus in circuit1.buses.values()])
    angles   = np.array([bus.delta for bus in circuit1.buses.values()])

    mismatch_vector = circuit1.settings.compute_power_mismatch(
        circuit1.buses, circuit1.ybus, voltages
    )
    print("\nMismatch vector:")
    print(mismatch_vector)

    #Jacobian (flat start)
    jac = Jacobian(circuit1)
    J = jac.calc_jacobian(circuit1.buses, circuit1.ybus, angles, voltages)

    print("\nJacobian matrix (flat start):")
    formatter = JacobianFormat(jac)
    formatter.print_dataframe()

    #Dimension Check
    print("\nMismatch vector length:", len(mismatch_vector))
    print("Jacobian shape:", J.shape)
    assert J.shape[0] == len(mismatch_vector), "Dimension mismatch!"
    assert J.shape[1] == len(mismatch_vector), "Dimension mismatch!"
    print("Dimensions match ✓")

    # Jacobian at PowerWorld Converged Solution
    converged_voltages = np.array([1.00000, 0.83377, 1.05000, 1.01930, 0.97429])
    converged_angles   = np.array([0.00, -22.41, -0.60, -2.83, -4.55])  # degrees

    J_converged = jac.calc_jacobian(
        circuit1.buses, circuit1.ybus, converged_angles, converged_voltages
    )

    print("\nJacobian at converged solution (compare against PowerWorld):")
    formatter.print_dataframe()