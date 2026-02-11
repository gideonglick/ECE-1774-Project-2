class TransmissionLine:
    def __init__(self, name, bus1_name:str, bus2_name:str, r:float, x:float, g:float, b:float):
        self.name = name
        self.bus1_name = bus1_name
        self.bus2_name = bus2_name
        self.r = r
        self.x = x
        self.g = g
        self.b = b
