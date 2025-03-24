class TaiKhoanDTO:
    MNV: int
    MK: str 
    TDN: str
    MNQ: int 
    TT: int

    def __init__(self, MNV, MK, TDN, MNQ, TT):
        self.MNV = MNV
        self.MK = MK
        self.TDN = TDN
        self.MNQ = MNQ
        self.TT = TT

    def MNV(self):
        return self.MNV
    
    def MNV(self, new_MNV):
        self.MNV = new_MNV

    def MK(self):
        return self.MK
    
    def MK(self, new_MK):
        self.MK = new_MK
    
    def TDN(self):
        return self.TDN
    
    def TDN(self, new_TDN):
        self.TDN = new_TDN
    
    def MNQ(self):
        return self.MNQ
    
    def MNQ(self, new_MNQ):
        self.MNQ = new_MNQ
    
    def TT(self):
        return self.TT
    
    def TT(self, new_TT):
        self.TT = new_TT
    
    def __eq__(self, other):
        if isinstance(other):
            return self.MNV == other.MNV and self.MK == other.MK and self.TDN == other.TDN and self.MNQ == other.MNQ
        return False