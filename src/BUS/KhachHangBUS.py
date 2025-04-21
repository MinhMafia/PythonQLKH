from DAO.KhachHangDAO import KhachHangDAO

class KhachHangBUS:
    def __init__(self):
        self.listKhachHang = KhachHangDAO.select_all()

    def get_khach_hang_all(self):
        return self.listKhachHang

    def get_khach_hang(self, index):
        return self.listKhachHang[index]

    def get_khach_hang_by_makh(self, makh):
        for index, kh in enumerate(self.listKhachHang):
            if kh.MKH == makh:
                return index
        return -1

    def add_khach_hang(self, kh):
        KhachHangDAO.insert(kh)

    def update_khach_hang(self, kh):
        # KhachHangDAO.update(kh)
        dao = KhachHangDAO()  # Tạo instance của KhachHangDAO
        dao.update(kh)        # Gọi phương thức update thông qua instance

    def delete_khach_hang(self, makh):
        KhachHangDAO.delete(makh)

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
        KhachHangDAO.update_email_by_makh(makh, new_email)

    def find_khach_hang_by_ma_khach_hang(self, ma_khach_hang):
        # return next((kh for kh in self.listKhachHang if kh.MKH == ma_khach_hang), None)
        return KhachHangDAO.select_by_id(ma_khach_hang) #khởi tạo mới để có dữ liệu mới nhất khi làm gì đó

    def kt(self, email):
        return KhachHangDAO.is_account_inactive(email)
