class Transformer:

    def __init__(self, name:str, bus1_name: str, bus2_name:str, r:float, x:float):
        self.name = name
        self.bus1_name = bus1_name
        self.bus2_name = bus2_name
        self.r = r
        self.x = x