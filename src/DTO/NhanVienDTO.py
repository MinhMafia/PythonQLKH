class NhanVienDTO:
    MNV: int         # Mã nhân viên
    HOTEN: str       # Họ và tên nhân viên
    GIOITINH: int    # Giới tính (0: Nữ, 1: Nam, v.v.)
    NGAYSINH: str    # Ngày sinh (định dạng yyyy-mm-dd)
    SDT: str         # Số điện thoại
    EMAIL: str       # Email
    MCV: int         # Mã chức vụ
    TT: int          # Trạng thái

    def __init__(self, MNV, HOTEN, GIOITINH, NGAYSINH, SDT, EMAIL, MCV, TT):
        self.MNV = MNV
        self.HOTEN = HOTEN
        self.GIOITINH = GIOITINH
        self.NGAYSINH = NGAYSINH
        self.SDT = SDT
        self.EMAIL = EMAIL
        self.MCV = MCV
        self.TT = TT

    # Getter và Setter
    def get_MNV(self):
        return self.MNV

    def set_MNV(self, new_MNV):
        self.MNV = new_MNV

    def get_HOTEN(self):
        return self.HOTEN

    def set_HOTEN(self, new_HOTEN):
        self.HOTEN = new_HOTEN

    def get_GIOITINH(self):
        return self.GIOITINH

    def set_GIOITINH(self, new_GIOITINH):
        self.GIOITINH = new_GIOITINH

    def get_NGAYSINH(self):
        return self.NGAYSINH

    def set_NGAYSINH(self, new_NGAYSINH):
        self.NGAYSINH = new_NGAYSINH

    def get_SDT(self):
        return self.SDT

    def set_SDT(self, new_SDT):
        self.SDT = new_SDT

    def get_EMAIL(self):
        return self.EMAIL

    def set_EMAIL(self, new_EMAIL):
        self.EMAIL = new_EMAIL

    def get_MCV(self):
        return self.MCV

    def set_MCV(self, new_MCV):
        self.MCV = new_MCV

    def get_TT(self):
        return self.TT

    def set_TT(self, new_TT):
        self.TT = new_TT

    def __eq__(self, other):
        if not isinstance(other, NhanVienDTO):
            return False
        return (
            self.MNV == other.MNV and
            self.HOTEN == other.HOTEN and
            self.GIOITINH == other.GIOITINH and
            self.NGAYSINH == other.NGAYSINH and
            self.SDT == other.SDT and
            self.EMAIL == other.EMAIL and
            self.MCV == other.MCV and
            self.TT == other.TT
        )
    
        def __str__(self):
            return f"MNV: {self.MNV}, HOTEN: {self.HOTEN}, GIOITINH: {self.GIOITINH}, NGAYSINH: {self.NGAYSINH}, SDT: {self.SDT}, EMAIL: {self.EMAIL}, MCV: {self.MCV}, TT: {self.TT}"
