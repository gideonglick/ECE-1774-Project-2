import numpy as np
from jacobian import Jacobian


class PowerFlow:
    def __init__(self, circuit):
        self.circuit = circuit
        self.settings = circuit.settings
        self.jacobian = Jacobian(circuit)
        self.converged = False
        self.iterations = 0
        self.final_mismatch = None

    def solve(self, buses, ybus, tol=0.001, max_iter=50):
        voltages = np.array([bus.vpu for bus in buses.values()], dtype=float)
        angles = np.array([bus.delta for bus in buses.values()], dtype=float)

        self.converged = False
        self.iterations = 0

        for iteration in range(1, max_iter + 1):
            mismatch_vector = self.settings.compute_power_mismatch(
                buses, ybus, voltages, angles
            )

            self.final_mismatch = mismatch_vector

            if np.max(np.abs(mismatch_vector)) < tol:
                self.converged = True
                self.iterations = iteration
                break

            J = self.jacobian.calc_jacobian(buses, ybus, angles, voltages)

            delta_x = np.linalg.solve(J, mismatch_vector)

            k = 0

            for bus in buses.values():
                if bus.bus_type != "Slack":
                    angles[bus.bus_index] += np.rad2deg(delta_x[k])
                    k += 1

            for bus in buses.values():
                if bus.bus_type == "PQ":
                    voltages[bus.bus_index] += delta_x[k]
                    k += 1

            self.iterations = iteration

        for bus in buses.values():
            bus.vpu = voltages[bus.bus_index]
            bus.delta = angles[bus.bus_index]

        return voltages, angles, self.converged, self.iterations