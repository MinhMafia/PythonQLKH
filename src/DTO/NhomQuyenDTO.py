class NhomQuyenDTO:
    def __init__(self, MNQ, TEN, TT):
        self.MNQ = MNQ  # Mã nhóm quyền
        self.TEN = TEN  # Tên nhóm quyền
        self.TT = TT    # Trạng thái

    # Getter và Setter cho MNQ
    def get_MNQ(self):
        return self.MNQ

    def set_MNQ(self, new_MNQ):
        self.MNQ = new_MNQ

    # Getter và Setter cho TEN
    def get_TEN(self):
        return self.TEN

    def set_TEN(self, new_TEN):
        self.TEN = new_TEN

    # Getter và Setter cho TT
    def get_TT(self):
        return self.TT

    def set_TT(self, new_TT):
        self.TT = new_TT


    def __str__(self):
        return f"NhomQuyenDTO(MNQ={self.MNQ}, TEN={self.TEN}, TT={self.TT})"