class GiaoDichDTO:
    MGD: int           # Mã giao dịch
    MKH: int           # Mã khách hàng
    MNV: int           # Mã nhân viên
    NGAYGIAODICH: str  # Ngày giao dịch (dùng str dạng 'YYYY-MM-DD HH:MM:SS')
    TIEN: int          # Số tiền giao dịch
    TIENKH: int        # Số tiền khách hàng tại thời điểm giao dịch
    TT: int            # Trạng thái

    def __init__(self, MGD, MKH, MNV, NGAYGIAODICH, TIEN, TIENKH, TT=1):
        self.MGD = MGD
        self.MKH = MKH
        self.MNV = MNV
        self.NGAYGIAODICH = NGAYGIAODICH
        self.TIEN = TIEN
        self.TIENKH = TIENKH
        self.TT = TT

    # Getter và Setter cho MGD
    def get_MGD(self):
        return self.MGD

    def set_MGD(self, new_MGD):
        self.MGD = new_MGD

    # Getter và Setter cho MKH
    def get_MKH(self):
        return self.MKH

    def set_MKH(self, new_MKH):
        self.MKH = new_MKH

    # Getter và Setter cho MNV
    def get_MNV(self):
        return self.MNV

    def set_MNV(self, new_MNV):
        self.MNV = new_MNV

    # Getter và Setter cho NGAYGIAODICH
    def get_NGAYGIAODICH(self):
        return self.NGAYGIAODICH

    def set_NGAYGIAODICH(self, new_NGAYGIAODICH):
        self.NGAYGIAODICH = new_NGAYGIAODICH

    # Getter và Setter cho TIEN
    def get_TIEN(self):
        return self.TIEN

    def set_TIEN(self, new_TIEN):
        self.TIEN = new_TIEN

    # Getter và Setter cho TIENKH
    def get_TIENKH(self):
        return self.TIENKH

    def set_TIENKH(self, new_TIENKH):
        self.TIENKH = new_TIENKH

    # Getter và Setter cho TT
    def get_TT(self):
        return self.TT

    def set_TT(self, new_TT):
        self.TT = new_TT

    # Hàm so sánh 2 đối tượng
    def __eq__(self, other):
        if not isinstance(other, GiaoDichDTO):
            return False
        return (
            self.MGD == other.MGD and
            self.MKH == other.MKH and
            self.MNV == other.MNV and
            self.NGAYGIAODICH == other.NGAYGIAODICH and
            self.TIEN == other.TIEN and
            self.TIENKH == other.TIENKH and
            self.TT == other.TT
        )
