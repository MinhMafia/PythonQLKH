from DAO.NhanVienDAO import NhanVienDAO

class NhanVienBUS:
    def __init__(self):
        self.listNhanVien = NhanVienDAO.get_instance().select_all()

    def get_nhan_vien_all(self):
        return NhanVienDAO.get_instance().select_all()

    def get_nhan_vien(self, index):
        return self.listNhanVien[index]

    def get_nhan_vien_by_mnv(self, mnv):
        for index, nv in enumerate(self.listNhanVien):
            if nv.MNV == mnv:
                return index
        return -1

    def add_nhan_vien(self, nv):
        return NhanVienDAO.get_instance().insert(nv)

    def update_nhan_vien(self, nv):
        return NhanVienDAO.get_instance().update(nv)

    def delete_nhan_vien(self, mnv):
        return NhanVienDAO.get_instance().delete(mnv)

    def search(self, txt, type):
        txt = txt.lower()
        result = []
        if type == "Tất cả":
            result = [
                nv for nv in self.listNhanVien 
                if txt in str(nv.MNV) or txt in nv.HOTEN.lower() or txt in nv.EMAIL.lower()
            ]
        elif type == "Mã nhân viên":
            result = [nv for nv in self.listNhanVien if txt in str(nv.MNV)]
        elif type == "Họ tên":
            result = [nv for nv in self.listNhanVien if txt in nv.HOTEN.lower()]
        elif type == "Email":
            result = [nv for nv in self.listNhanVien if txt in nv.EMAIL.lower()]
        return result

    def doi_email(self, mnv, new_email):
        nv = NhanVienDAO.select_by_id(mnv)
        if nv:
            nv.EMAIL = new_email
            return NhanVienDAO.get_instance().update(nv)
        return 0

    def find_nhan_vien_by_ma_nhan_vien(self, ma_nhan_vien):
        return next((nv for nv in self.get_nhan_vien_all() if nv.MNV == ma_nhan_vien), None)

    def kt(self, email):
        return NhanVienDAO.is_account_inactive(email)
