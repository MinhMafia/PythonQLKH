from DAO.NhomQuyenDAO import NhomQuyenDAO

class NhomQuyenBUS:
    def __init__(self):
        self.nhom_quyen_list = NhomQuyenDAO.select_all()

    def get_all_nhom_quyen(self):
        """Lấy danh sách tất cả nhóm quyền"""
        return NhomQuyenDAO.select_all()
    def get_nhom_quyen_by_mnq(self, mnq):
        """Lấy thông tin nhóm quyền dựa trên mã nhóm quyền"""
        return NhomQuyenDAO.select_by_mnq(mnq)
    def add_nhom_quyen(self, nhom_quyen_dto):
        """Thêm nhóm quyền mới"""
        return NhomQuyenDAO.insert(nhom_quyen_dto)

    def get_ten_nhom_quyen_by_mnq(self, mnq):
        """Lấy tên nhóm quyền dựa trên mã nhóm quyền"""
        nhom_quyen = NhomQuyenDAO.select_by_mnq(mnq)
        return nhom_quyen.TEN if nhom_quyen else "Không xác định"
    
    def delete_nhom_quyen(self, mnq):
        """Xóa nhóm quyền dựa trên mã nhóm quyền"""
        return NhomQuyenDAO.delete(mnq)
