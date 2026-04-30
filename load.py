from settings import Settings

class Load:
    def __init__(self, name: str, bus1_name: str, mw: float, mvar: float, settings: Settings,
                 zp: float = 0.0, ip: float = 0.0, pp: float = 1.0,
                 zq: float = 0.0, iq: float = 0.0, pq: float = 1.0):
        self.name = name
        self.bus1_name = bus1_name
        self.mw = mw
        self.mvar = mvar
        self.settings = settings

        # ZIP percentages for real power
        self.zp = zp
        self.ip = ip
        self.pp = pp

        # ZIP percentages for reactive power
        self.zq = zq
        self.iq = iq
        self.pq = pq

    def calc_p(self, vpu: float = 1.0):
        if self.settings.use_zip:
            return (self.mw / self.settings.sbase) * (self.zp * vpu**2 + self.ip * vpu + self.pp)

        return self.mw / self.settings.sbase

    def calc_q(self, vpu: float = 1.0):
        if self.settings.use_zip:
            return (self.mvar / self.settings.sbase) * (self.zq * vpu**2 + self.iq * vpu + self.pq)

        return self.mvar / self.settings.sbase