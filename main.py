"""
ECE 1774 Project 2 -- Final
Shunt compensation enhancement, validated against:
  1. Glover Example 6.9   (5-bus power flow base case)
  2. Glover Example 6.9 + 200 MVAR cap at Bus 2  (integration sanity check)
  3. Glover Example 15.3  (numerical validation of compensator math)
"""

from circuit import Circuit
from powerflow import PowerFlow
from bus import Bus
import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.float_format', lambda x: f'{x:.4f}')


# ============================================================
# CASE 1 / 2: Glover Example 6.9 (base + compensated)
# ============================================================

def build_case_69(compensation_mvar: float = 0.0,
                  compensation_bus: str = "Bus 2") -> Circuit:
    """Glover Example 6.9 (and Example 6.10 in some editions)."""
    Bus.bus_counter = 0
    case = Circuit("Case 6.9", s_base=100.0)

    case.add_bus("Bus 1", 15.0,  "Slack", vpu=1.000)
    case.add_bus("Bus 2", 345.0, "PQ")
    case.add_bus("Bus 3", 15.0,  "PV",    vpu=1.050)
    case.add_bus("Bus 4", 345.0, "PQ")
    case.add_bus("Bus 5", 345.0, "PQ")

    case.add_transformer("T1", "Bus 1", "Bus 5", 0.00150, 0.02)
    case.add_transformer("T2", "Bus 3", "Bus 4", 0.00075, 0.01)

    case.add_transmission_line("Line 1", "Bus 2", "Bus 4", 0.0090,  0.100, 0, 1.72)
    case.add_transmission_line("Line 2", "Bus 2", "Bus 5", 0.0045,  0.050, 0, 0.88)
    case.add_transmission_line("Line 3", "Bus 4", "Bus 5", 0.00225, 0.025, 0, 0.44)

    case.add_generator("G1", "Bus 1", 1.000, 0.0)
    case.add_generator("G2", "Bus 3", 1.050, 520.0)

    case.add_load("Load 2", "Bus 2", 800.0, 280.0)
    case.add_load("Load 4", "Bus 4",  80.0,  40.0)

    if compensation_mvar > 0:
        case.add_shunt_compensator("C1", compensation_bus, compensation_mvar)

    return case


def voltage_table(circuit: Circuit) -> pd.DataFrame:
    return pd.DataFrame(
        [{"Bus": b.name,
          "Type": b.bus_type,
          "|V| (pu)": b.vpu,
          "Angle (deg)": b.delta}
         for b in circuit.buses.values()]
    )


def total_real_losses_mw(circuit: Circuit) -> float:
    """Total real losses = sum of real power injections (steady state)."""
    ybus = circuit.ybus.values
    n = len(circuit.buses)
    V = np.zeros(n, dtype=complex)
    for bus in circuit.buses.values():
        V[bus.bus_index] = bus.vpu * np.exp(1j * np.deg2rad(bus.delta))
    I = ybus @ V
    S = V * np.conj(I)
    return np.sum(S.real) * circuit.s_base


def run_case_69():
    print("\n" + "=" * 70)
    print("VALIDATION 1: Glover Example 6.9 -- 5-bus base case")
    print("=" * 70)
    case_base = build_case_69(compensation_mvar=0.0)
    case_base.calc_ybus()
    pf = PowerFlow(case_base)
    pf.solve(tol=0.001, max_iter=50)
    print(f"Converged in {pf.iterations} iterations\n")
    print(voltage_table(case_base).to_string(index=False))
    print(f"\nTotal real losses: {total_real_losses_mw(case_base):.3f} MW")

    print("\n" + "=" * 70)
    print("VALIDATION 2: Glover Example 6.9 with 200 MVAR shunt cap at Bus 2")
    print("=" * 70)
    case_comp = build_case_69(compensation_mvar=200.0, compensation_bus="Bus 2")
    case_comp.calc_ybus()
    pf2 = PowerFlow(case_comp)
    pf2.solve(tol=0.001, max_iter=50)
    print(f"Converged in {pf2.iterations} iterations\n")
    print(voltage_table(case_comp).to_string(index=False))
    print(f"\nTotal real losses: {total_real_losses_mw(case_comp):.3f} MW")

    # Comparison table
    print("\n" + "-" * 70)
    print("Voltage comparison (base vs. compensated)")
    print("-" * 70)
    base_v = {b.name: b.vpu for b in case_base.buses.values()}
    comp_v = {b.name: b.vpu for b in case_comp.buses.values()}
    df = pd.DataFrame([
        {"Bus": name,
         "|V| base": base_v[name],
         "|V| comp": comp_v[name],
         "Delta |V|": comp_v[name] - base_v[name]}
        for name in base_v
    ])
    print(df.to_string(index=False))


# ============================================================
# CASE 3: Glover Example 15.3 -- numerical validation of compensator
# ============================================================

# System base for 15.3
S_BASE_15 = 10.0       # MVA
V_BASE_15 = 13.8       # kV LL
Z_BASE_15 = V_BASE_15**2 / S_BASE_15  # = 19.044 ohm

# Feeder impedance: 3 + j6 ohm/phase
R_LINE_15_PU = 3.0 / Z_BASE_15        # 0.15753
X_LINE_15_PU = 6.0 / Z_BASE_15        # 0.31506


def build_15_3(load_mw: float, load_mvar: float, cap_mvar: float = 0.0) -> Circuit:
    """
    Glover Example 15.3: 13.8 kV primary feeder with shunt cap at load bus.

    Note: The textbook uses a constant-impedance load (R || jX in ohms).
    Our simulator uses constant-power loads. We give it the textbook's
    converged P, Q values for each operating point so each scenario is
    self-consistent at that voltage.
    """
    Bus.bus_counter = 0
    case = Circuit("Glover 15.3", s_base=S_BASE_15)

    case.add_bus("Source",  V_BASE_15, "Slack", vpu=1.05)  # 5% above rated
    case.add_bus("LoadBus", V_BASE_15, "PQ")

    case.add_transmission_line("Feeder", "Source", "LoadBus",
                               R_LINE_15_PU, X_LINE_15_PU, 0.0, 0.0)
    case.add_load("Load", "LoadBus", load_mw, load_mvar)

    if cap_mvar > 0:
        case.add_shunt_compensator("Cap", "LoadBus", cap_mvar)

    return case


def run_case_15_3():
    """Validate compensator against Example 15.3 published numbers."""
    print("\n" + "=" * 70)
    print("VALIDATION 3: Glover Example 15.3 -- numerical compensator check")
    print("=" * 70)

    I_BASE_KA = S_BASE_15 / (np.sqrt(3) * V_BASE_15)  # 0.4184 kA per phase

    def line_current_ka(circuit):
        Vs = circuit.buses["Source"]
        Vl = circuit.buses["LoadBus"]
        V_s = Vs.vpu * np.exp(1j * np.deg2rad(Vs.delta))
        V_l = Vl.vpu * np.exp(1j * np.deg2rad(Vl.delta))
        Z = complex(R_LINE_15_PU, X_LINE_15_PU)
        I_pu = (V_s - V_l) / Z
        return abs(I_pu) * I_BASE_KA

    # Part (a): no capacitor
    case_a = build_15_3(load_mw=6.033, load_mvar=3.017, cap_mvar=0.0)
    case_a.calc_ybus()
    PowerFlow(case_a).solve(tol=1e-6, max_iter=50)
    v_a = case_a.buses["LoadBus"].vpu * V_BASE_15
    i_a = line_current_ka(case_a)

    # Part (b): with cap (X_C = 40 ohm/phase Y-connected)
    # Q_3phase at rated V_LL = V_LL^2 / X_C = 13.8^2 / 40 = 4.761 MVAR
    case_b = build_15_3(load_mw=7.430, load_mvar=3.715, cap_mvar=4.761)
    case_b.calc_ybus()
    PowerFlow(case_b).solve(tol=1e-6, max_iter=50)
    v_b = case_b.buses["LoadBus"].vpu * V_BASE_15
    i_b = line_current_ka(case_b)

    df = pd.DataFrame([
        {"Quantity": "V_load (no cap), kV",
         "Textbook": 10.980, "Computed": v_a, "Error %": 100*(v_a-10.980)/10.980},
        {"Quantity": "I_line (no cap), kA",
         "Textbook": 0.3545, "Computed": i_a, "Error %": 100*(i_a-0.3545)/0.3545},
        {"Quantity": "V_load (with cap), kV",
         "Textbook": 12.190, "Computed": v_b, "Error %": 100*(v_b-12.190)/12.190},
        {"Quantity": "I_line (with cap), kA",
         "Textbook": 0.3520, "Computed": i_b, "Error %": 100*(i_b-0.3520)/0.3520},
    ])
    print(df.to_string(index=False))


def main():
    run_case_69()
    run_case_15_3()


if __name__ == "__main__":
    main()