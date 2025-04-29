class CTQuyenDTO:
    MNQ: int          # Mã nhóm quyền
    MCN: str          # Mã chức năng
    HANHDONG: str     # Hành động thực hiện

    def __init__(self, MNQ, MCN, HANHDONG):
        self.MNQ = MNQ
        self.MCN = MCN
        self.HANHDONG = HANHDONG

    # Getter và Setter cho MNQ
    def get_MNQ(self):
        return self.MNQ

    def set_MNQ(self, new_MNQ):
        self.MNQ = new_MNQ

    # Getter và Setter cho MCN
    def get_MCN(self):
        return self.MCN

    def set_MCN(self, new_MCN):
        self.MCN = new_MCN

    # Getter và Setter cho HANHDONG
    def get_HANHDONG(self):
        return self.HANHDONG

    def set_HANHDONG(self, new_HANHDONG):
        self.HANHDONG = new_HANHDONG

    # Hàm so sánh 2 đối tượng
    def __eq__(self, other):
        if not isinstance(other, CTQuyenDTO):
            return False
        return (
            self.MNQ == other.MNQ and
            self.MCN == other.MCN and
            self.HANHDONG == other.HANHDONG
        )
