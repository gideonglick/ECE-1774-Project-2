class TransmissionLine:
    def __init__(self, bus1_name:str, bus2_name:str, r:float, x:float, g:float, b:float):
        self.bus = bus1_name
        self.bus2 = bus2_name
        self.r = r
        self.x = x
        self.g = g
        self.b = b
