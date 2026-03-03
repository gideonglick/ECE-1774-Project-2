import pandas as pd

class Transformer:

    def __init__(self, name:str, bus1_name: str, bus2_name:str, r:float, x:float):
        self.name = name
        self.bus1_name = bus1_name
        self.bus2_name = bus2_name
        self.r = r
        self.x = x

        self.z_series = complex(self.r, self.x)
        if self.z_series == 0:
            raise ValueError("r and x cannot both be zero.")
        self.Yseries = 1 / self.z_series

    def calc_yprim(self) -> pd.DataFrame:
        Y = self.Yseries
        labels = [self.bus1_name, self.bus2_name]

        yprim = pd.DataFrame(
            [[Y, -Y],
             [-Y, Y]],
            index=labels,
            columns=labels,
        )

        return yprim