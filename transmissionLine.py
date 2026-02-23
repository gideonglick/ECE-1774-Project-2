import pandas as pd

class TransmissionLine:
    def __init__(self, name, bus1_name:str, bus2_name:str, r:float, x:float, g:float, b:float):
        self.name = name
        self.bus1_name = bus1_name
        self.bus2_name = bus2_name
        self.r = r
        self.x = x
        self.g = g
        self.b = b

        self.z_series = complex(self.r, self.x)
        if self.z_series == 0:
            raise ValueError("r and x cannot both be zero.")
        self.Yseries = 1 / self.z_series
        self.Yshunt = complex(self.g, self.b)

    def calc_yprim(self) -> pd.DataFrame:
        Yser = self.Yseries
        Yshu = self.Yshunt
        labels = [self.bus1_name, self.bus2_name]

        yprim = pd.DataFrame(
            [[Yser+Yshu/2, -Yser],
            [-Yser, Yser+Yshu/2]],
            index=labels,
            columns=labels,
            )

        return yprim


