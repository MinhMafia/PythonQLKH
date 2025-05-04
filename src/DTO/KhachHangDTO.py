class KhachHangDTO:
    MKH: int         # Mã khách hàng
    HOTEN: str       # Họ và tên
    NGAYTHAMGIA: str # Ngày tham gia (dùng kiểu str cho đơn giản, format YYYY-MM-DD)
    DIACHI: str      # Địa chỉ
    SDT: str         # Số điện thoại
    EMAIL: str       # Email
    CCCD: int        # Số căn cước công dân
    TIEN: int        # Số tiền khách hàng có
    TT: int          # Trạng thái

    def __init__(self, MKH, HOTEN, NGAYTHAMGIA, DIACHI, SDT, EMAIL, CCCD, TIEN, TT=1):
        self.MKH = MKH
        self.HOTEN = HOTEN
        self.NGAYTHAMGIA = NGAYTHAMGIA
        self.DIACHI = DIACHI
        self.SDT = SDT
        self.EMAIL = EMAIL
        self.CCCD = CCCD
        self.TIEN = TIEN
        self.TT = TT

    # Getter và Setter cho MKH
    def get_MKH(self):
        return self.MKH

    def set_MKH(self, new_MKH):
        self.MKH = new_MKH

    # Getter và Setter cho HOTEN
    def get_HOTEN(self):
        return self.HOTEN

    def set_HOTEN(self, new_HOTEN):
        self.HOTEN = new_HOTEN

    # Getter và Setter cho NGAYTHAMGIA
    def get_NGAYTHAMGIA(self):
        return self.NGAYTHAMGIA

    def set_NGAYTHAMGIA(self, new_NGAYTHAMGIA):
        self.NGAYTHAMGIA = new_NGAYTHAMGIA

    # Getter và Setter cho DIACHI
    def get_DIACHI(self):
        return self.DIACHI

    def set_DIACHI(self, new_DIACHI):
        self.DIACHI = new_DIACHI

    # Getter và Setter cho SDT
    def get_SDT(self):
        return self.SDT

    def set_SDT(self, new_SDT):
        self.SDT = new_SDT

    # Getter và Setter cho EMAIL
    def get_EMAIL(self):
        return self.EMAIL

    def set_EMAIL(self, new_EMAIL):
        self.EMAIL = new_EMAIL

    # Getter và Setter cho CCCD
    def get_CCCD(self):
        return self.CCCD

    def set_CCCD(self, new_CCCD):
        self.CCCD = new_CCCD

    # Getter và Setter cho TIEN
    def get_TIEN(self):
        return self.TIEN

    def set_TIEN(self, new_TIEN):
        self.TIEN = new_TIEN

    # Getter và Setter cho TT
    def get_TT(self):
        return self.TT

    def set_TT(self, new_TT):
        self.TT = new_TT

    # Hàm so sánh 2 đối tượng
    def __eq__(self, other):
        if not isinstance(other, KhachHangDTO):
            return False
        return (
            self.MKH == other.MKH and
            self.HOTEN == other.HOTEN and
            self.NGAYTHAMGIA == other.NGAYTHAMGIA and
            self.DIACHI == other.DIACHI and
            self.SDT == other.SDT and
            self.EMAIL == other.EMAIL and
            self.CCCD == other.CCCD and
            self.TIEN == other.TIEN and
            self.TT == other.TT
        )
    
    def __str__(self):
        return f"{self.MKH} {self.HOTEN} {self.SDT} {self.EMAIL} {self.CCCD} {self.DIACHI}"

