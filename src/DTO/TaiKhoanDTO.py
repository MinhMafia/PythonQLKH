class TaiKhoanDTO:
    MNV: int
    MK: str 
    TDN: str
    MNQ: int 
    TT: int

    def __init__(self, MNV, TDN, MK, MNQ, TT):
        self.MNV = MNV
        self.MK = MK
        self.TDN = TDN
        self.MNQ = MNQ
        self.TT = TT

    def get_MNV(self):
        return self.MNV
    
    def set_MNV(self, new_MNV):
        self.MNV = new_MNV

    def get_MK(self):
        return self.MK
    
    def set_MK(self, new_MK):
        self.MK = new_MK
    
    def get_TDN(self):
        return self.TDN
    
    def set_TDN(self, new_TDN):
        self.TDN = new_TDN
    
    def get_MNQ(self):
        return self.MNQ
    
    def set_MNQ(self, new_MNQ):
        self.MNQ = new_MNQ
    
    def get_TT(self):
        return self.TT
    
    def set_TT(self, new_TT):
        self.TT = new_TT
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):  # Kiểm tra other có cùng class không
            return False
        return (
            self.MNV == other.MNV and
            self.MK == other.MK and
            self.TDN == other.TDN and
            self.MNQ == other.MNQ
        )