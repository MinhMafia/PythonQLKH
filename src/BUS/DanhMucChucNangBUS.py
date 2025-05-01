from DAO.DanhMucChucNangDAO import DanhMucChucNangDAO

class DanhMucChucNangBUS:
    def __init__(self):
        self.chuc_nang_list = DanhMucChucNangDAO.select_all()

    def get_all_chuc_nang(self):
        """Lấy danh sách tất cả danh mục chức năng"""
        return self.chuc_nang_list