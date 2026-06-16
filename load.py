from settings import Settings

class Load:
    def __init__(self, name: str, bus1_name: str, mw:float, mvar:float, settings: Settings):
        self.name = name
        self.bus1_name = bus1_name
        self.mw = mw
        self.mvar = mvar
        self.settings = settings

    def calc_p(self):
        return self.mw/self.settings.sbase

    def calc_q(self):
        return self.mvar / self.settings.sbase

