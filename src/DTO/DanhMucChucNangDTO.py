class DanhMucChucNangDTO:
    def __init__(self, MCN, TEN):
        self.MCN = MCN  # Mã chức năng
        self.TEN = TEN  # Tên chức năng

    # Getter và Setter cho MCN
    def get_MCN(self):
        return self.MCN

    def set_MCN(self, new_MCN):
        self.MCN = new_MCN

    # Getter và Setter cho TEN
    def get_TEN(self):
        return self.TEN

    def set_TEN(self, new_TEN):
        self.TEN = new_TEN

    def __dict__(self):
        return {"MCN": self.MCN, "TEN": self.TEN}