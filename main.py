from bus import Bus
from generator import Generator
from load import Load
from transformer import Transformer
from transmissionLine import TransmissionLine

def main():

    #Testing Bus class
    bus1 = Bus("Bus1", 20.0)
    bus2 = Bus("Bus2", 230.0)

    print(bus1.name, bus1.nominal_kv, bus1.bus_index)
    print(bus2.name, bus2.nominal_kv, bus2.bus_index)

    #Testing Transformer Class
    t1 = Transformer("T1", "Bus1", "Bus2", .01, .1)
    print(t1.name, t1.bus1_name, t1.bus2_name, t1.r, t1.x)

    #Testing Transmission Line class
    line1 = TransmissionLine("Line1", "Bus1", "Bus2", .02, .25, 0, .04)
    print(line1.name, line1.bus1_name, line1.bus2_name, line1.r, line1.x, line1.g, line1.b)

    #Testing Load Class
    load1 = Load("Load1", "Bus2", 50.0, 30.0)
    print(load1.name, load1.bus1_name, load1.mw, load1.mvar)

    #Testing Generator Class
    gen1 = Generator("G1", "Bus1", 1.04, 100.0)
    print(gen1.name, gen1.bus1_name, gen1.voltage_setpoint, gen1.mw_setpoint)

if __name__ == "__main__":
    main()