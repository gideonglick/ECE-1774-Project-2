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

    # Newton-Raphson Power Flow
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
            self.final_mismatch = mismatch

            if np.max(np.abs(mismatch)) < tol:
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

        if not self.converged:
            raise ValueError("Newton-Raphson did not converge")

        for bus in buses.values():
            bus.vpu = voltages[bus.bus_index]
            bus.delta = angles[bus.bus_index]

        return voltages, angles, self.converged, self.iterations

    # Fault Study
    def calc_ybus_faulted(self):
        # Always rebuild clean Ybus first, then stamp generator shunts
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
            columns=ybus_faulted.columns
        )
        return self.zbus

    def solve_fault(self, fault_bus_name: str):
        if fault_bus_name not in self.circuit.buses:
            raise ValueError(f"Bus '{fault_bus_name}' not found in circuit.")

        ybus_faulted = self.calc_ybus_faulted()
        self.calc_zbus(ybus_faulted)

        # Use actual prefault voltage from power flow solution
        vf = complex(self.circuit.buses[fault_bus_name].vpu)
        Z_nn = self.zbus.loc[fault_bus_name, fault_bus_name]
        self.fault_current = vf / Z_nn

        self.bus_voltages = {}
        for bus_name in self.circuit.buses.keys():
            Z_kn = self.zbus.loc[bus_name, fault_bus_name]
            V_k_prefault = complex(self.circuit.buses[bus_name].vpu)
            self.bus_voltages[bus_name] = V_k_prefault - (Z_kn / Z_nn) * vf

        print(f"\n--- Fault Study Results ---")
        print(f"Faulted Bus   : {fault_bus_name}")
        print(f"Prefault V    : {abs(vf):.4f} pu")
        print(f"Fault Current : {abs(self.fault_current):.4f} pu  "
              f"(angle: {np.angle(self.fault_current, deg=True):.2f} deg)")
        print(f"\nPost-Fault Bus Voltages:")

        rows = []
        for bus_name, V in self.bus_voltages.items():
            rows.append({
                "Bus": bus_name,
                "Voltage (pu)": round(abs(V), 4),
                "Angle (deg)": round(np.angle(V, deg=True), 2)
            })
            print(f"  {bus_name}: {abs(V):.4f} pu  ({np.angle(V, deg=True):.2f} deg)")

        return pd.DataFrame(rows)