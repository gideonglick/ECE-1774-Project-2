import numpy as np
import pandas as pd
from circuit import Circuit


class Jacobian:

    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.buses = circuit.buses
        self.ybus = circuit.ybus

        # Sort by bus_index so ordering matches the Ybus matrix rows/cols
        self.ordered_buses = sorted(self.buses.values(), key=lambda bus: bus.bus_index)

        # Slack bus is excluded from the Jacobian entirely
        self.angle_buses = [bus for bus in self.ordered_buses if bus.bus_type != "Slack"]

        # PV buses have fixed voltage so they are excluded from voltage magnitude cols/rows
        self.voltage_buses = [bus for bus in self.ordered_buses if bus.bus_type == "PQ"]

        self.num_pv = sum(1 for bus in self.ordered_buses if bus.bus_type == "PV")

        # (2N - 2 - N_PV): remove 2 for slack (P and Q), remove 1 per PV bus (Q only)
        self.size = (2 * len(self.ordered_buses)) - 2 - self.num_pv

        self.J1 = None  # dP/d_delta
        self.J2 = None  # dP/d|V|
        self.J3 = None  # dQ/d_delta
        self.J4 = None  # dQ/d|V|
        self.J  = None  # Full assembled Jacobian

    def _calc_J1(self, angles, voltages):
        # J1 is square: rows and cols = all non-slack buses (PQ + PV)
        # Answers: "if I change the angle at bus j, how much does real power at bus i change?"
        n = len(self.angle_buses)
        J1 = np.zeros((n, n))

        for row, bus_i in enumerate(self.angle_buses):
            i = bus_i.bus_index
            Vi = voltages[i]
            delta_i = angles[i]

            # Pi and Qi at bus_i needed for the diagonal term formulas
            Pi, Qi = self.circuit.settings.compute_power_injection(bus_i, self.ybus, voltages, angles)

            # Diagonal susceptance of bus i — self-susceptance, only used in diagonal term
            Bii = self.ybus.iloc[i, i].imag

            for col, bus_j in enumerate(self.angle_buses):
                j = bus_j.bus_index
                Vj = voltages[j]
                delta_j = angles[j]

                # Conductance and susceptance between bus i and bus j
                # If buses are not connected, both are zero and J1 entry will be zero
                Gij = self.ybus.iloc[i, j].real
                Bij = self.ybus.iloc[i, j].imag

                # Angle difference between bus i and j — drives power flow between them
                d = delta_i - delta_j

                if i == j:
                    # Diagonal term
                    J1[row, col] = -Qi - Bii * Vi ** 2
                else:
                    # Off-diagonal: how Pi changes when delta_j (a different bus) changes
                    J1[row, col] = Vi * Vj * (Gij * np.sin(d) - Bij * np.cos(d))

        return J1

    def _calc_J2(self, angles, voltages):
        # J2 is non-square: rows = all non-slack, cols = PQ only
        n_rows = len(self.angle_buses)
        n_cols = len(self.voltage_buses)
        J2 = np.zeros((n_rows, n_cols))

        for row, bus_i in enumerate(self.angle_buses):
            i = bus_i.bus_index
            Vi = voltages[i]
            delta_i = angles[i]
            Pi, Qi = self.circuit.settings.compute_power_injection(bus_i, self.ybus, voltages, angles)
            Gii = self.ybus.iloc[i, i].real

            for col, bus_j in enumerate(self.voltage_buses):
                j = bus_j.bus_index
                Vj = voltages[j]
                delta_j = angles[j]
                Gij = self.ybus.iloc[i, j].real
                Bij = self.ybus.iloc[i, j].imag
                d = delta_i - delta_j

                if i == j:
                    J2[row, col] = Pi / Vi + Gii * Vi
                else:
                    J2[row, col] = Vi * (Gij * np.cos(d) + Bij * np.sin(d))

        return J2

    def _calc_J3(self, angles, voltages):
        # J3 is non-square: rows = PQ only, cols = all non-slack
        n_rows = len(self.voltage_buses)
        n_cols = len(self.angle_buses)
        J3 = np.zeros((n_rows, n_cols))

        for row, bus_i in enumerate(self.voltage_buses):
            i = bus_i.bus_index
            Vi = voltages[i]
            delta_i = angles[i]
            Pi, Qi = self.circuit.settings.compute_power_injection(bus_i, self.ybus, voltages, angles)
            Gii = self.ybus.iloc[i, i].real

            for col, bus_j in enumerate(self.angle_buses):
                j = bus_j.bus_index
                Vj = voltages[j]
                delta_j = angles[j]
                Gij = self.ybus.iloc[i, j].real
                Bij = self.ybus.iloc[i, j].imag
                d = delta_i - delta_j

                if i == j:
                    J3[row, col] = Pi - Gii * Vi ** 2
                else:
                    J3[row, col] = -Vi * Vj * (Gij * np.cos(d) + Bij * np.sin(d))

        return J3

    def _calc_J4(self, angles, voltages):
        # J4 is square: rows and cols = PQ buses only
        n = len(self.voltage_buses)
        J4 = np.zeros((n, n))

        for row, bus_i in enumerate(self.voltage_buses):
            i = bus_i.bus_index
            Vi = voltages[i]
            delta_i = angles[i]
            Pi, Qi = self.circuit.settings.compute_power_injection(bus_i, self.ybus, voltages, angles)
            Bii = self.ybus.iloc[i, i].imag

            for col, bus_j in enumerate(self.voltage_buses):
                j = bus_j.bus_index
                Vj = voltages[j]
                delta_j = angles[j]
                Gij = self.ybus.iloc[i, j].real
                Bij = self.ybus.iloc[i, j].imag
                d = delta_i - delta_j

                if i == j:
                    J4[row, col] = Qi / Vi - Bii * Vi
                else:
                    J4[row, col] = Vi * (Gij * np.sin(d) - Bij * np.cos(d))

        return J4

    def calc_jacobian(self, buses, ybus, angles, voltages):
        # Trig functions require radians — angles are passed in as degrees
        angles_rad = np.deg2rad(angles)

        self.J1 = self._calc_J1(angles_rad, voltages)
        self.J2 = self._calc_J2(angles_rad, voltages)
        self.J3 = self._calc_J3(angles_rad, voltages)
        self.J4 = self._calc_J4(angles_rad, voltages)

        # Stack submatrices into full Jacobian: [ J1  J2 ]
        #                                       [ J3  J4 ]
        self.J = np.block([[self.J1, self.J2],
                           [self.J3, self.J4]])
        return self.J


class JacobianFormat:

    def __init__(self, jacobian_obj: Jacobian):
        self.jacobian_obj = jacobian_obj

    def to_dataframe(self):
        row_labels  = [f"P {bus.name}" for bus in self.jacobian_obj.angle_buses]
        row_labels += [f"Q {bus.name}" for bus in self.jacobian_obj.voltage_buses]
        col_labels  = [f"δ {bus.name}" for bus in self.jacobian_obj.angle_buses]
        col_labels += [f"V {bus.name}" for bus in self.jacobian_obj.voltage_buses]

        return pd.DataFrame(
            self.jacobian_obj.J,
            index=row_labels,
            columns=col_labels
        )

    def print_dataframe(self, decimals=4):
        print(self.to_dataframe().round(decimals))