from circuit import Circuit
from transformer import Transformer
from transmissionLine import TransmissionLine

def main():

    transformer1 = Transformer("T1", "Bus 1", "Bus 2", 0.01, 0.10)
    print(transformer1.Yseries)
    print(transformer1.calc_yprim())

    transformer2 = Transformer("T2", "Bus A", "Bus B", 0.0, 0.20)
    print(transformer2.Yseries)
    print(transformer2.calc_yprim())

    transformer3 = Transformer("T3", "Bus X", "Bus Y", 0.5, 0.01)
    print(transformer3.Yseries)
    print(transformer3.calc_yprim())

    line1 = TransmissionLine("Line 1", "Bus 1", "Bus 2", 0.02, 0.25, 0.0, 0.04)
    print(line1.Yseries, line1.Yshunt)
    print(line1.calc_yprim())

    line2 = TransmissionLine("Line 2", "Bus 3", "Bus 4", 0.05, 0.20, 0.0, 0.0)
    print(line2.Yseries, line2.Yshunt)
    print(line2.calc_yprim())

    line3 = TransmissionLine("Line 3", "Bus 5", "Bus 6", 0.01, 0.15, 0.0, 0.20)
    print(line3.Yseries, line3.Yshunt)
    print(line3.calc_yprim())

if __name__ == "__main__":
    main()
