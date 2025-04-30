from DAO.KhachHangDAO import KhachHangDAO

class KhachHangBUS:
    def __init__(self):
        self.dao = KhachHangDAO()
        self.listKhachHang = self.dao.select_all()
        # print("KhachHangBUS init listKhachHang:", [c.__dict__ for c in self.listKhachHang])  # Log khởi tạo

    def get_khach_hang_all(self):
        self.listKhachHang = self.dao.select_all()  # Làm mới danh sách
        # print("get_khach_hang_all result:", [c.__dict__ for c in self.listKhachHang])  # Log dữ liệu trả về
        return self.listKhachHang

    def get_khach_hang(self, index):
        return self.listKhachHang[index]

    def get_khach_hang_by_makh(self, makh):
        for index, kh in enumerate(self.listKhachHang):
            if kh.MKH == makh:
                return index
        return -1

    def add_khach_hang(self, kh):
        result = self.dao.insert(kh)
        if result:
            self.listKhachHang = self.dao.select_all()  # Làm mới danh sách
            # print("add_khach_hang updated listKhachHang:", [c.__dict__ for c in self.listKhachHang])  # Log
        return result

    def update_khach_hang(self, kh):
        result = self.dao.update(kh)
        if result:
            self.listKhachHang = self.dao.select_all()  # Làm mới danh sách
            # print("update_khach_hang updated listKhachHang:", [c.__dict__ for c in self.listKhachHang])  # Log
        return result

    def delete_khach_hang(self, makh):
        result = self.dao.delete(makh)
        if result:
            self.listKhachHang = self.dao.select_all()  # Làm mới danh sách
            # print("delete_khach_hang updated listKhachHang:", [c.__dict__ for c in self.listKhachHang])  # Log
        return result

    def find_khach_hang_by_cccd(self, cccd):
        customer = self.dao.select_by_cccd(cccd)
        # print("find_khach_hang_by_cccd CCCD=", cccd, "result:", customer.__dict__ if customer else None)  # Log
        return customer

    def search(self, txt, type):
        txt = txt.lower()
        result = []
        if type == "Tất cả":
            result = [kh for kh in self.listKhachHang if txt in str(kh.MKH) or txt in kh.HOTEN.lower() or txt in kh.EMAIL.lower()]
        elif type == "Mã khách hàng":
            result = [kh for kh in self.listKhachHang if txt in str(kh.MKH)]
        elif type == "Họ tên":
            result = [kh for kh in self.listKhachHang if txt in kh.HOTEN.lower()]
        elif type == "Email":
            result = [kh for kh in self.listKhachHang if txt in kh.EMAIL.lower()]
        return result

    def doi_email(self, makh, new_email):
        self.dao.update_email_by_makh(makh, new_email)
        self.listKhachHang = self.dao.select_all()  # Làm mới danh sách
        # print("doi_email updated listKhachHang:", [c.__dict__ for c in self.listKhachHang])  # Log

    def find_khach_hang_by_ma_khach_hang(self, ma_khach_hang):
        customer = self.dao.select_by_id(ma_khach_hang)
        # print("find_khach_hang_by_ma_khach_hang MKH=", ma_khach_hang, "result:", customer.__dict__ if customer else None)  # Log
        return customer

    def kt(self, email):
        is_inactive = self.dao.is_account_inactive(email)
        # print("kt email=", email, "is_inactive:", is_inactive)  # Log
        return is_inactive