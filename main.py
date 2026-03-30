from settings import Settings
from circuit import Circuit
from bus import Bus
from generator import Generator
from load import Load
from jacobian import Jacobian, JacobianFormatter
import numpy as np

if __name__ == "__main__":
    Bus.bus_counter = 0

    circuit1 = Circuit("Mismatch Test")
    circuit1.settings = Settings()
    circuit1.settings.circuit = circuit1

    circuit1.buses["Bus 1"] = Bus("Bus 1", 230.0, "Slack", 1.05, 0.0)
    circuit1.buses["Bus 2"] = Bus("Bus 2", 230.0, "PQ", 0.98, -0.08)
    circuit1.buses["Bus 3"] = Bus("Bus 3", 230.0, "PV", 1.02, 0.12)

    circuit1.add_transmission_line("Line 1", "Bus 1", "Bus 2", 0.02, 0.06, 0.0, 0.03)
    circuit1.add_transmission_line("Line 2", "Bus 2", "Bus 3", 0.08, 0.24, 0.0, 0.025)
    circuit1.add_transformer("T1", "Bus 1", "Bus 3", 0.01, 0.04)

    circuit1.generators["G1"] = Generator("G1", "Bus 3", 1.02, 120.0, circuit1.settings)
    circuit1.loads["L1"] = Load("L1", "Bus 2", 90.0, 30.0, circuit1.settings)

    circuit1.calc_ybus()

    print("Ybus:")
    print(circuit1.ybus)

    # --- Mismatch Vector ---
    voltages = np.array([bus.vpu   for bus in circuit1.buses.values()])
    angles   = np.array([bus.delta for bus in circuit1.buses.values()])

    mismatch_vector = circuit1.settings.compute_power_mismatch(circuit1.buses, circuit1.ybus, voltages)
    print("\nMismatch vector:")
    print(mismatch_vector)

    # --- Jacobian ---
    jac = Jacobian(circuit1)
    J = jac.calc_jacobian(circuit1.buses, circuit1.ybus, angles, voltages)

    print("\nJacobian matrix:")
    formatter = JacobianFormatter(jac)
    formatter.print_dataframe()

    # --- Dimension Check ---
    print("\nMismatch vector length:", len(mismatch_vector))
    print("Jacobian shape:", J.shape)
    assert J.shape[0] == len(mismatch_vector), "Dimension mismatch!"
    assert J.shape[1] == len(mismatch_vector), "Dimension mismatch!"
    print("Dimensions match ✓")