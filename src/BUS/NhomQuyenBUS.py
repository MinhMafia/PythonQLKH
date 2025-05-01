from DAO.NhomQuyenDAO import NhomQuyenDAO
from BUS.ChiTietQuyenBUS import CTQuyenBUS

class NhomQuyenBUS:
    def __init__(self):
        self.nhom_quyen_list = NhomQuyenDAO.select_all()
        self.ct_quyen_bus = CTQuyenBUS()

    def get_all_nhom_quyen(self):
        """Lấy danh sách tất cả nhóm quyền"""
        return NhomQuyenDAO.select_all()

    def get_nhom_quyen_by_mnq(self, mnq):
        """Lấy thông tin nhóm quyền dựa trên mã nhóm quyền"""
        return NhomQuyenDAO.select_by_mnq(mnq)

    def add_nhom_quyen(self, nhom_quyen_dto):
        """Thêm nhóm quyền mới, trả về mnq"""
        return NhomQuyenDAO.insert(nhom_quyen_dto)

    def update_nhom_quyen(self, nhom_quyen_dto):
        """Cập nhật nhóm quyền"""
        return NhomQuyenDAO.update(nhom_quyen_dto)

    def delete_nhom_quyen(self, mnq):
        """Xóa nhóm quyền và các chi tiết quyền liên quan"""
        # Xóa các chi tiết quyền trước
        self.ct_quyen_bus.delete_all_by_mnq(mnq)
        # Xóa nhóm quyền
        return NhomQuyenDAO.delete(mnq)

    def get_ten_nhom_quyen_by_mnq(self, mnq):
        """Lấy tên nhóm quyền dựa trên mã nhóm quyền"""
        nhom_quyen = NhomQuyenDAO.select_by_mnq(mnq)
        return nhom_quyen.TEN if nhom_quyen else "Không xác định"