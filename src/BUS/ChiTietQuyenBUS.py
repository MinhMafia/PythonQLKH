from DAO.CTQuyenDAO import CTQuyenDAO
from DTO.CTQuyenDTO import CTQuyenDTO

class CTQuyenBUS:
    def __init__(self):
        # Lấy danh sách tất cả các chi tiết quyền từ DAO
        self.listCTQuyen = CTQuyenDAO.select_all()

    def get_ct_quyen_all(self):
        # Trả về danh sách tất cả chi tiết quyền
        return self.listCTQuyen

    def get_ct_quyen(self, index):
        # Trả về chi tiết quyền theo chỉ số trong danh sách
        return self.listCTQuyen[index]

    def get_ct_quyen_by_mnq(self, mnq):
        # Tìm chi tiết quyền theo Mã nhóm quyền (MNQ)
        return [ctq for ctq in self.listCTQuyen if ctq.MNQ == mnq]

    def get_ct_quyen_by_mcn(self, mcn):
        # Tìm chi tiết quyền theo Mã chức năng (MCN)
        return [ctq for ctq in self.listCTQuyen if ctq.MCN == mcn]

    def add_ct_quyen(self, ctq):
        # Thêm một chi tiết quyền mới
        CTQuyenDAO.insert(ctq)

    def update_ct_quyen(self, ctq):
        # Cập nhật chi tiết quyền
        dao = CTQuyenDAO()  # Tạo instance của CTQuyenDAO
        dao.update(ctq)     # Gọi phương thức update thông qua instance

    def delete_ct_quyen(self, mnq, mcn, hanh_dong):
        # Xóa chi tiết quyền (thực tế là không có trong schema nhưng có thể đánh dấu hoặc xóa)
        CTQuyenDAO.delete(mnq, mcn, hanh_dong)

    def search(self, txt, type):
        # Tìm kiếm chi tiết quyền theo các tiêu chí
        txt = txt.lower()
        result = []
        if type == "Tất cả":
            result = [ctq for ctq in self.listCTQuyen if txt in str(ctq.MNQ) or txt in ctq.MCN.lower() or txt in ctq.HANHDONG.lower()]
        elif type == "Mã nhóm quyền":
            result = [ctq for ctq in self.listCTQuyen if txt in str(ctq.MNQ)]
        elif type == "Mã chức năng":
            result = [ctq for ctq in self.listCTQuyen if txt in ctq.MCN.lower()]
        elif type == "Hành động":
            result = [ctq for ctq in self.listCTQuyen if txt in ctq.HANHDONG.lower()]
        return result

    def find_ct_quyen_by_mnq_mcn(self, mnq, mcn):
        # Tìm chi tiết quyền theo Mã nhóm quyền và Mã chức năng
        return CTQuyenDAO.select_by_mnq_mcn(mnq, mcn)

