from DAO.TaiKhoanDAO import TaiKhoanDAO
# from DAO.NhomQuyenDAO import NhomQuyenDAO

class TaiKhoanBUS:
    def __init__(self):
        self.listTaiKhoan = TaiKhoanDAO.select_all()
        # self.nhomQuyenDAO = NhomQuyenDAO()

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

    # def get_nhom_quyen_dto(self, manhom):
    #     return self.nhomQuyenDAO.select_by_id(str(manhom))

    def add_acc(self, tk):
        TaiKhoanDAO.insert(tk)

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
        TaiKhoanDAO.update_pass_by_mnv(id, new_password)

    def find_tai_khoan_by_ma_nhan_vien(self, ma_nhan_vien):
        return next((tk for tk in self.get_tai_khoan_all() if tk.MNV == ma_nhan_vien), None)

    def kt(self, username):
            return TaiKhoanDAO.is_account_inactive(username)