import cmath
import numpy as np
import pandas as pd
from circuit import Circuit
from jacobian import Jacobian


class PowerFlow:

    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.settings = circuit.settings
        self.jacobian = Jacobian(circuit)
        self.converged = False
        self.iterations = 0
        self.final_mismatch = None
        self.zbus = None
        self.fault_current = None
        self.bus_voltages = None

    # ---------- helpers ----------
    @staticmethod
    def _bus_phasor(bus):
        """Convert a bus's (|V|, delta[deg]) into a complex phasor."""
        return bus.vpu * cmath.exp(1j * np.deg2rad(bus.delta))

    # ---------- Newton-Raphson Power Flow ----------
    def solve(self, tol=0.001, max_iter=50):
        self.circuit.calc_ybus()
        buses = self.circuit.buses
        ybus = self.circuit.ybus

        voltages = np.array([bus.vpu for bus in buses.values()], dtype=float)
        angles = np.array([bus.delta for bus in buses.values()], dtype=float)

        self.converged = False
        self.iterations = 0

        for iteration in range(1, max_iter + 1):
            mismatch = self.settings.compute_power_mismatch(
                buses, ybus, voltages, angles
            )

            if np.max(np.abs(mismatch)) < tol:
                self.final_mismatch = mismatch
                self.converged = True
                self.iterations = iteration
                break

            J = self.jacobian.calc_jacobian(buses, ybus, angles, voltages)
            delta_x = np.linalg.solve(J, mismatch)

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
            self.final_mismatch = mismatch

        if not self.converged:
            raise ValueError("Newton-Raphson did not converge")

        # Write converged solution back onto the bus objects
        for bus in buses.values():
            bus.vpu = voltages[bus.bus_index]
            bus.delta = angles[bus.bus_index]

        return voltages, angles, self.converged, self.iterations

    # ---------- Fault Study ----------
    def calc_ybus_faulted(self):
        """Rebuild clean Ybus, then stamp generator subtransient shunts."""
        self.circuit.calc_ybus()
        bus_names = list(self.circuit.buses.keys())
        bus_index = {name: i for i, name in enumerate(bus_names)}
        ybus_matrix = self.circuit.ybus.values.copy()

        for gen in self.circuit.generators.values():
            if gen.xd_subtransient > 0:
                i = bus_index[gen.bus1_name]
                y_gen = 1.0 / (1j * gen.xd_subtransient)
                ybus_matrix[i, i] += y_gen

        return pd.DataFrame(ybus_matrix, index=bus_names, columns=bus_names)

    def calc_zbus(self, ybus_faulted):
        self.zbus = pd.DataFrame(
            np.linalg.inv(ybus_faulted.values),
            index=ybus_faulted.index,
            columns=ybus_faulted.columns,
        )
        return self.zbus

    def solve_fault(self, fault_bus_name: str,
                    fault_impedance: complex = 0.0,
                    prefault_voltage: complex = None):

        if fault_bus_name not in self.circuit.buses:
            raise ValueError(f"Bus '{fault_bus_name}' not found in circuit.")

        ybus_faulted = self.calc_ybus_faulted()
        self.calc_zbus(ybus_faulted)

        # Determine prefault voltage at the faulted bus
        if prefault_voltage is not None:
            vf = complex(prefault_voltage)
        else:
            vf = self._bus_phasor(self.circuit.buses[fault_bus_name])

        Z_nn = self.zbus.loc[fault_bus_name, fault_bus_name]

        # Subtransient fault current
        self.fault_current = vf / (Z_nn + fault_impedance)

        # Post-fault bus voltages via Thevenin superposition
        self.bus_voltages = {}
        for bus_name in self.circuit.buses.keys():
            Z_kn = self.zbus.loc[bus_name, fault_bus_name]
            if prefault_voltage is not None:
                V_k_prefault = complex(prefault_voltage)
            else:
                V_k_prefault = self._bus_phasor(self.circuit.buses[bus_name])
            self.bus_voltages[bus_name] = (
                V_k_prefault - (Z_kn / (Z_nn + fault_impedance)) * vf
            )

        return self.bus_voltages