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
        """
        run_fault        : run a fault study after the power flow
        fault_all_buses  : fault every bus one at a time, print N x N grid
        prefault_voltage : flat complex phasor (e.g. 1.05+0j) applied at all
                           buses for the fault study. If None, use power-flow
                           solution.
        skip_power_flow  : skip Newton-Raphson entirely. Use for lossless
                           + unloaded systems (Example 8.5) where NR would
                           fail and there is nothing to solve.
        """
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

        mag_grid = pd.DataFrame(index=bus_names, columns=bus_names, dtype=float)
        ang_grid = pd.DataFrame(index=bus_names, columns=bus_names, dtype=float)
        fault_currents = {}

        for faulted in bus_names:
            self.pf.solve_fault(faulted, prefault_voltage=prefault_voltage)
            fault_currents[faulted] = self.pf.fault_current
            for bus_name, V in self.pf.bus_voltages.items():
                mag_grid.loc[faulted, bus_name] = abs(V)
                ang_grid.loc[faulted, bus_name] = np.angle(V, deg=True)

        # Voltage magnitudes -- 4 decimals everywhere
        self._print_section_header("Post-Fault Bus Voltage Magnitudes (pu)")
        print("  rows = faulted bus   |   cols = bus being measured\n")
        print(mag_grid.to_string(float_format=lambda x: f"{x:8.4f}"))
        print()

        # Voltage angles -- 2 decimals everywhere
        self._print_section_header("Post-Fault Bus Voltage Angles (deg)")
        print("  rows = faulted bus   |   cols = bus being measured\n")
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