from DAO.TaiKhoanDAO import TaiKhoanDAO
from DTO.TaiKhoanDTO import TaiKhoanDTO

class TaiKhoanBUS:
    def __init__(self):
        self.listTaiKhoan = TaiKhoanDAO.select_all()

    def get_tai_khoan_all():
        return TaiKhoanDAO.select_all()

    def get_tai_khoan(self, index):
        return self.listTaiKhoan[index]

    def get_tai_khoan_by_manv(self, manv):
        for index, tk in enumerate(self.listTaiKhoan):
            if tk.MNV == manv:
                return index
        return -1

    def get_tai_khoan_by_makh(self, manv):
        for index, tk in enumerate(self.listTaikhoanKH):
            if tk.MNV == manv:
                return index
        return -1

    def add_acc(self, tk):
        account = TaiKhoanDTO(
            MNV=tk["MNV"],
            TDN=tk["TDN"],
            MK=tk.get("MK", ""),
            MNQ=tk["MNQ"],
            TT=tk["TT"]
        )
        print(f"TaiKhoanBUS: Creating account - MNV: {account.MNV}, TDN: {account.TDN}, MK: {account.MK}, MNQ: {account.MNQ}, TT: {account.TT}")
        TaiKhoanDAO().insert(account)  # Sửa ở đây


    def update_acc(self, tk):
        TaiKhoanDAO.update(tk)

    def check_tdn(self, tdn):
        tk = TaiKhoanDAO.select_by_user(tdn)
        return tk is None

    def delete_acc(self, manv):
        TaiKhoanDAO.delete(manv)

    def search(self, txt, type):
        txt = txt.lower()
        result = []
        if type == "Tất cả":
            result = [tk for tk in self.listTaiKhoan if txt in str(tk.MNV) or txt in tk.TDN.lower()]
        elif type == "Mã nhân viên":
            result = [tk for tk in self.listTaiKhoan if txt in str(tk.MNV)]
        elif type == "Tên đăng nhập":
            result = [tk for tk in self.listTaiKhoan if txt in tk.TDN.lower()]
        return result

    def doi_mat_khau(self, id, new_password):
        from BUS.NhanVienBUS import NhanVienBUS
        nhanvien_bus = NhanVienBUS()
        nhanvien = nhanvien_bus.find_nhan_vien_by_ma_nhan_vien(id)
        if nhanvien and nhanvien.EMAIL:
            result = TaiKhoanDAO.get_instance().update_pass(nhanvien.EMAIL, new_password)
            return result
        else:
            raise Exception("Không tìm thấy email của nhân viên để cập nhật mật khẩu!")

    def find_tai_khoan_by_ma_nhan_vien(self, ma_nhan_vien):
        return next((tk for tk in self.get_tai_khoan_all() if tk.MNV == ma_nhan_vien), None)

    def kt(self, username):
        return TaiKhoanDAO.is_account_inactive(username)