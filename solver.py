import numpy as np
from jacobian import Jacobian, JacobianFormat
from powerflow import PowerFlow


class Solver:
    def __init__(self, circuit):
        self.circuit = circuit
        self.circuit.calc_ybus()
        self.pf = PowerFlow(circuit)

        self.converged = False
        self.iterations = 0
        self.mismatch_norm = None
        self.solved_voltages = None
        self.solved_angles = None
        self.fault_bus = "Bus 3"
        self.fault_results = None
        self.faulted_voltage = None
        self.fault_current_mag = None
        self.mismatch_vector = None
        self.mismatch_table = None
        self.solved_mismatch_table = None
        self.jacobian_matrix = None
        self.jacobian_formatter = None

    def run(self, force_print=False, run_fault=False):
        self.run_power_flow()

        blackout = False

        if run_fault:
            self.run_fault_study()

        if blackout and not force_print:
            print("BLACKOUT")
            return

        self.print_power_flow_results()

        if run_fault:
            self.print_fault_results()

    def run_power_flow(self):
        flat_voltages = np.array(
            [bus.vpu for bus in self.circuit.buses.values()],
            dtype=float
        )
        flat_angles = np.array(
            [bus.delta for bus in self.circuit.buses.values()],
            dtype=float
        )

        self.mismatch_vector = self.circuit.settings.compute_power_mismatch(
            self.circuit.buses,
            self.circuit.ybus,
            flat_voltages,
            flat_angles
        )

        self.mismatch_table = self.circuit.settings.compute_mismatch_table(
            self.circuit.buses,
            self.circuit.ybus,
            flat_voltages,
            flat_angles
        )

        jac = Jacobian(self.circuit)
        self.jacobian_matrix = jac.calc_jacobian(
            self.circuit.buses,
            self.circuit.ybus,
            flat_angles,
            flat_voltages
        )

        self.jacobian_formatter = JacobianFormat(jac)

        assert self.jacobian_matrix.shape[0] == len(self.mismatch_vector), "Dimension mismatch!"
        assert self.jacobian_matrix.shape[1] == len(self.mismatch_vector), "Dimension mismatch!"

        self.solved_voltages, self.solved_angles, self.converged, self.iterations = self.pf.solve(
            tol=0.001,
            max_iter=50
        )

        self.mismatch_norm = np.max(np.abs(self.pf.final_mismatch))

        self.solved_mismatch_table = self.circuit.settings.compute_mismatch_table(
            self.circuit.buses,
            self.circuit.ybus,
            self.solved_voltages,
            self.solved_angles
        )

    def run_fault_study(self):
        self.circuit.generators["Gen1"].xd_subtransient = 0.20
        self.circuit.generators["Gen3"].xd_subtransient = 0.20

        self.pf.calc_ybus_faulted()
        self.fault_results = self.pf.solve_fault(fault_bus_name=self.fault_bus)

        self.faulted_voltage = abs(self.pf.bus_voltages[self.fault_bus])
        self.fault_current_mag = abs(self.pf.fault_current)

    def print_power_flow_results(self):

        print("\nMismatch table (flat start):")
        print(self.mismatch_table.to_string(index=False))

        print("\nJacobian matrix (flat start):")
        self.jacobian_formatter.print_dataframe()

        print("\nJacobian shape:", self.jacobian_matrix.shape)
        print("Jacobian dimensions match mismatch vector")

        print("\nSolved Bus Results:")
        for bus in self.circuit.buses.values():
            print(f"  {bus.name}: V = {bus.vpu:.5f} pu, angle = {bus.delta:.5f} deg")

        print(f"\nConverged: {self.converged}")
        print(f"Iterations: {self.iterations}")
        print(f"Final mismatch norm: {self.mismatch_norm}")

        print("\nMismatch table at solution:")
        print(self.solved_mismatch_table.to_string(index=False))

    def print_fault_results(self):
        print("\nFault Study Results:")
        print(self.fault_results.to_string(index=False))
        print(f"\nFaulted bus: {self.fault_bus}")
        print(f"Faulted bus voltage: {self.faulted_voltage:.6f} pu")
        print(f"Fault current magnitude: {self.fault_current_mag:.6f} pu")