import pandas as pd


class ShuntCompensator:
    """
    Shunt reactive power compensator (capacitor or reactor).

    Sign convention for mvar_rating:
        positive  -> capacitor (injects reactive power, +jB)
        negative  -> reactor   (absorbs reactive power, -jB)

    The device is modeled as a pure shunt admittance added to the
    diagonal entry of Y-bus at its connected bus.

    In per-unit on the system MVA base:
        B_pu = mvar_rating / s_base
        Y_pu = j * B_pu     (sign carried by mvar_rating)
    """

    def __init__(self, name: str, bus1_name: str, mvar_rating: float, s_base: float = 100.0):
        self.name = name
        self.bus1_name = bus1_name
        self.mvar_rating = mvar_rating  # signed MVAR (+ cap, - reactor)
        self.s_base = s_base

        # Per-unit susceptance on system base
        self.b_pu = self.mvar_rating / self.s_base

        # Per-unit shunt admittance (purely imaginary)
        self.Yshunt = complex(0.0, self.b_pu)

    def calc_yprim(self) -> pd.DataFrame:
        """
        Returns the 1x1 primitive admittance for this shunt element.
        It will be stamped onto the (bus1, bus1) diagonal of Y-bus.
        """
        labels = [self.bus1_name]
        yprim = pd.DataFrame(
            [[self.Yshunt]],
            index=labels,
            columns=labels,
        )
        return yprim