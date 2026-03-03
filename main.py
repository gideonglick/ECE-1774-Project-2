from circuit import Circuit
from transformer import Transformer
from transmissionLine import TransmissionLine
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.float_format', lambda x: f'{x:.4f}')

def main():
    # Case 6.9 - Five Bus System
    case69 = Circuit("Case 6.9")

    # Add 5 buses
    case69.add_bus("Bus 1", 15.0)
    case69.add_bus("Bus 2", 345.0)
    case69.add_bus("Bus 3", 15.0)
    case69.add_bus("Bus 4", 345.0)
    case69.add_bus("Bus 5", 345.0)

    # Add transformers (Table 6.3)
    case69.add_transformer("T1", "Bus 1", "Bus 5", 0.00150, 0.02)
    case69.add_transformer("T2", "Bus 3", "Bus 4", 0.00075, 0.01)

    # Add transmission lines (Table 6.2)
    case69.add_transmission_line("Line 1", "Bus 2", "Bus 4", 0.0090, 0.100, 0, 1.72)
    case69.add_transmission_line("Line 2", "Bus 2", "Bus 5", 0.0045, 0.050, 0, 0.88)
    case69.add_transmission_line("Line 3", "Bus 4", "Bus 5", 0.00225, 0.025, 0, 0.44)

    # Calculate Ybus
    case69.calc_ybus()
    print(case69.ybus)
if __name__ == "__main__":
    main()
