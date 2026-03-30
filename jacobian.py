import numpy as np
import pandas as pd
from circuit import Circuit


class Jacobian:

    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.buses = circuit.buses
        self.ybus = circuit.ybus

        self.ordered_buses = sorted(self.buses.values(), key=lambda bus: bus.bus_index)
        self.angle_buses = [bus for bus in self.ordered_buses if bus.bus_type != "Slack"]
        self.voltage_buses = [bus for bus in self.ordered_buses if bus.bus_type == "PQ"]

        self.num_pv = sum(1 for bus in self.ordered_buses if bus.bus_type == "PV")
        self.size = (2 * len(self.ordered_buses)) - 2 - self.num_pv

        # Submatrices stored after calc_jacobian is called
        self.J1 = None
        self.J2 = None
        self.J3 = None
        self.J4 = None
        self.J = None

    def _calc_J1(self, angles, voltages):
        """dP/d_delta — rows: non-slack buses, cols: non-slack buses."""
        n = len(self.angle_buses)
        J1 = np.zeros((n, n))

        for row, bus_i in enumerate(self.angle_buses):
            i = bus_i.bus_index
            Vi = voltages[i]
            delta_i = angles[i]
            Pi, Qi = self.circuit.settings.compute_power_injection(bus_i, self.ybus, voltages, angles)
            Bii = self.ybus.iloc[i, i].imag

            for col, bus_j in enumerate(self.angle_buses):
                j = bus_j.bus_index
                Vj = voltages[j]
                delta_j = angles[j]
                Gij = self.ybus.iloc[i, j].real
                Bij = self.ybus.iloc[i, j].imag
                d = delta_i - delta_j

                if i == j:
                    J1[row, col] = -Qi - Bii * Vi ** 2
                else:
                    J1[row, col] = Vi * Vj * (Gij * np.sin(d) - Bij * np.cos(d))

        return J1

    def _calc_J2(self, angles, voltages):
        """dP/d|V| — rows: non-slack buses, cols: PQ buses."""
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
        """dQ/d_delta — rows: PQ buses, cols: non-slack buses."""
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
        """dQ/d|V| — rows: PQ buses, cols: PQ buses."""
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
        """
        Build the full Jacobian matrix J = [[J1, J2], [J3, J4]].

        Parameters:
            buses    : dict of Bus objects
            ybus     : pd.DataFrame Ybus (complex)
            angles   : np.array of voltage angles in degrees, indexed by bus_index
            voltages : np.array of voltage magnitudes, indexed by bus_index

        Returns:
            J : np.array of shape (size x size)
        """
        angles_rad = np.deg2rad(angles)

        self.J1 = self._calc_J1(angles_rad, voltages)
        self.J2 = self._calc_J2(angles_rad, voltages)
        self.J3 = self._calc_J3(angles_rad, voltages)
        self.J4 = self._calc_J4(angles_rad, voltages)

        self.J = np.block([[self.J1, self.J2],
                           [self.J3, self.J4]])
        return self.J


class JacobianFormatter:

    def __init__(self, jacobian_obj: Jacobian):
        self.jacobian_obj = jacobian_obj

    def to_dataframe(self):
        row_labels = [f"P {bus.name}" for bus in self.jacobian_obj.angle_buses]
        row_labels += [f"Q {bus.name}" for bus in self.jacobian_obj.voltage_buses]
        col_labels = [f"δ {bus.name}" for bus in self.jacobian_obj.angle_buses]
        col_labels += [f"V {bus.name}" for bus in self.jacobian_obj.voltage_buses]

        return pd.DataFrame(
            self.jacobian_obj.J,
            index=row_labels,
            columns=col_labels
        )

    def print_dataframe(self, decimals=4):
        print(self.to_dataframe().round(decimals))