import numpy as np
import pandas as pd
from powerflow import PowerFlow


class Solver:
    def __init__(self, circuit):
        self.circuit = circuit
        self.circuit.calc_ybus()
        self.pf = PowerFlow(circuit)
        self.converged = False
        self.iterations = 0
        self.mismatch_norm = None
        self.fault_bus = "Bus 1"
        self.fault_current_mag = None

    # ---------- Public entry point ----------
    def run(self, run_fault: bool = True,
            fault_all_buses: bool = False,
            prefault_voltage: complex = None,
            skip_power_flow: bool = False):

        self._print_case_banner()

        # --- Power Flow (optional) ---
        if skip_power_flow:
            print()
            print("  (Power flow skipped -- unloaded network, "
                  "flat prefault voltages)")
            print()
        else:
            try:
                self.pf.solve()
                self.converged = self.pf.converged
                self.iterations = self.pf.iterations
                self.mismatch_norm = float(
                    np.max(np.abs(self.pf.final_mismatch))
                )
            except ValueError:
                self.converged = False
            self._print_power_flow_results()

        # --- Fault Study ---
        if run_fault:
            if fault_all_buses:
                self._run_fault_all_buses(prefault_voltage=prefault_voltage)
            else:
                self.pf.solve_fault(
                    self.fault_bus,
                    prefault_voltage=prefault_voltage,
                )
                self.fault_current_mag = abs(self.pf.fault_current)
                self._print_single_fault_results()

    # ---------- Sweep every bus, build N x N grid ----------
    def _run_fault_all_buses(self, prefault_voltage=None):
        bus_names = list(self.circuit.buses.keys())

        # Build Ybus and Zbus once up front and display them
        ybus_faulted = self.pf.calc_ybus_faulted()
        zbus = self.pf.calc_zbus(ybus_faulted)

        self._print_section_header("Faulted Ybus (pu)")
        print("  Base Ybus with generator subtransient reactances stamped\n")
        print(self._format_complex_df(ybus_faulted))
        print()

        self._print_section_header("Zbus = inv(Ybus)  (pu)")
        print(self._format_complex_df(zbus))
        print()

        mag_grid = pd.DataFrame(index=bus_names, columns=bus_names, dtype=float)
        ang_grid = pd.DataFrame(index=bus_names, columns=bus_names, dtype=float)
        fault_currents = {}

        for faulted in bus_names:
            self.pf.solve_fault(faulted, prefault_voltage=prefault_voltage)
            fault_currents[faulted] = self.pf.fault_current
            for bus_name, V in self.pf.bus_voltages.items():
                # Row = bus being measured, Col = faulted bus
                # (matches Glover Table 8.7 layout)
                mag_grid.loc[bus_name, faulted] = abs(V)
                ang_grid.loc[bus_name, faulted] = np.angle(V, deg=True)

        # Voltage magnitudes -- 4 decimals everywhere
        self._print_section_header("Post-Fault Bus Voltage Magnitudes (pu)")
        print("  rows = bus being measured   |   cols = faulted bus\n")
        print(mag_grid.to_string(float_format=lambda x: f"{x:8.4f}"))
        print()

        # Voltage angles -- 2 decimals everywhere
        self._print_section_header("Post-Fault Bus Voltage Angles (deg)")
        print("  rows = bus being measured   |   cols = faulted bus\n")
        print(ang_grid.to_string(float_format=lambda x: f"{x:8.2f}"))
        print()

        # Fault currents
        self._print_section_header("Fault Currents (bolted 3-phase)")
        rows = []
        for bus_name, If in fault_currents.items():
            rows.append({
                "Faulted Bus": bus_name,
                "|If| (pu)": abs(If),
                "Angle (deg)": np.angle(If, deg=True),
            })
        df = pd.DataFrame(rows).set_index("Faulted Bus")
        print(df.to_string(
            formatters={
                "|If| (pu)":   lambda x: f"{x:10.4f}",
                "Angle (deg)": lambda x: f"{x:10.2f}",
            }
        ))
        print()

    # ---------- Printing helpers ----------
    @staticmethod
    def _format_complex_df(df):
        """Format a complex-valued DataFrame with aligned real+imag parts."""
        def fmt(z):
            r, i = z.real, z.imag
            # Keep very small values clean (floating-point dust -> 0)
            if abs(r) < 1e-9: r = 0.0
            if abs(i) < 1e-9: i = 0.0
            sign = "+" if i >= 0 else "-"
            return f"{r:8.4f} {sign} j{abs(i):7.4f}"
        return df.map(fmt).to_string()

    def _print_case_banner(self):
        bar = "#" * 70
        print()
        print(bar)
        print(f"#  CASE: {self.circuit.name}")
        print(bar)

    def _print_section_header(self, title):
        print()
        print("-" * 70)
        print(f"  {title}")
        print("-" * 70)

    def _print_power_flow_results(self):
        self._print_section_header("Power Flow Results")
        if not self.converged:
            print("  Power flow did NOT converge "
                  "(expected for unloaded validation cases)\n")
            return

        print(f"  Converged in {self.iterations} iterations  "
              f"(max |mismatch| = {self.mismatch_norm:.2e})\n")

        rows = []
        for bus in self.circuit.buses.values():
            rows.append({
                "Bus": bus.name,
                "V (pu)": bus.vpu,
                "Angle (deg)": bus.delta,
            })
        df = pd.DataFrame(rows).set_index("Bus")
        print(df.to_string(
            formatters={
                "V (pu)":      lambda x: f"{x:8.4f}",
                "Angle (deg)": lambda x: f"{x:8.2f}",
            }
        ))
        print()

    def _print_single_fault_results(self):
        If = self.pf.fault_current
        self._print_section_header(
            f"Fault Study -- bolted 3-phase fault at {self.fault_bus}"
        )
        print(f"  Fault current: {abs(If):.4f} pu  "
              f"(angle {np.angle(If, deg=True):.2f} deg)\n")

        rows = []
        for bus_name, V in self.pf.bus_voltages.items():
            rows.append({
                "Bus": bus_name,
                "V (pu)": abs(V),
                "Angle (deg)": np.angle(V, deg=True),
            })
        df = pd.DataFrame(rows).set_index("Bus")
        print(df.to_string(
            formatters={
                "V (pu)":      lambda x: f"{x:8.4f}",
                "Angle (deg)": lambda x: f"{x:8.2f}",
            }
        ))
        print()