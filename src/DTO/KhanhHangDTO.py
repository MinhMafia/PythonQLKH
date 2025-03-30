class KhachHangDTO:
    MKH: int         # Mã khách hàng
    HOTEN: str       # Họ và tên KH
    NGAYTHAMGIA: str # Ngày tạo dữ liệu
    DIACHI: str      # Địa chỉ
    SDT: str         # Số điện thoại
    EMAIL: str       # Email
    TT: int          # Trạng thái

    def __init__(self, MKH, HOTEN, NGAYTHAMGIA, DIACHI, SDT, EMAIL, TT):
        self.MKH = MKH
        self.HOTEN = HOTEN
        self.NGAYTHAMGIA = NGAYTHAMGIA
        self.DIACHI = DIACHI
        self.SDT = SDT
        self.EMAIL = EMAIL
        self.TT = TT

    # Getter và Setter
    def get_MKH(self):
        return self.MKH
    
    def set_MKH(self, new_MKH):
        self.MKH = new_MKH

    def get_HOTEN(self):
        return self.HOTEN
    
    def set_HOTEN(self, new_HOTEN):
        self.HOTEN = new_HOTEN

    def get_NGAYTHAMGIA(self):
        return self.NGAYTHAMGIA
    
    def set_NGAYTHAMGIA(self, new_NGAYTHAMGIA):
        self.NGAYTHAMGIA = new_NGAYTHAMGIA

    def get_DIACHI(self):
        return self.DIACHI
    
    def set_DIACHI(self, new_DIACHI):
        self.DIACHI = new_DIACHI

    def get_SDT(self):
        return self.SDT
    
    def set_SDT(self, new_SDT):
        self.SDT = new_SDT

    def get_EMAIL(self):
        return self.EMAIL
    
    def set_EMAIL(self, new_EMAIL):
        self.EMAIL = new_EMAIL

    def get_TT(self):
        return self.TT
    
    def set_TT(self, new_TT):
        self.TT = new_TT

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
            self.TT == other.TT
        )
