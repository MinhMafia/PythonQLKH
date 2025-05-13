class ChucVuDTO:
    MCV: int         # Mã chức vụ
    TEN: str         # Tên chức vụ
    MUCLUONG: int    # Mức lương
    TT: int          # Trạng thái

    def __init__(self, MCV, TEN, MUCLUONG, TT=1):
        self.MCV = MCV
        self.TEN = TEN
        self.MUCLUONG = MUCLUONG
        self.TT = TT

    # Getter và Setter cho MCV
    def get_MCV(self):
        return self.MCV

    def set_MCV(self, new_MCV):
        self.MCV = new_MCV

    # Getter và Setter cho TEN
    def get_TEN(self):
        return self.TEN

    def set_TEN(self, new_TEN):
        self.TEN = new_TEN

    # Getter và Setter cho MUCLUONG
    def get_MUCLUONG(self):
        return self.MUCLUONG

    def set_MUCLUONG(self, new_MUCLUONG):
        self.MUCLUONG = new_MUCLUONG

    # Getter và Setter cho TT
    def get_TT(self):
        return self.TT

    def set_TT(self, new_TT):
        self.TT = new_TT

    # Hàm so sánh 2 đối tượng
    def __eq__(self, other):
        if not isinstance(other, ChucVuDTO):
            return False
        return (
            self.MCV == other.MCV and
            self.TEN == other.TEN and
            self.MUCLUONG == other.MUCLUONG and
            self.TT == other.TT
        )
    
    
    def __str__(self):
        return f"ChucVuDTO(MCV={self.MCV}, TEN={self.TEN}, MUCLUONG={self.MUCLUONG}, TT={self.TT})"
