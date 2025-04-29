from DAO.ChucVuDAO import ChucVuDAO
from DTO.ChucVuDTO import ChucVuDTO

class ChucVuBUS:
    def __init__(self):
        # Lấy danh sách các chức vụ từ DAO
        self.listChucVu = ChucVuDAO.select_all()

    def get_chuc_vu_all(self):
        # Trả về danh sách tất cả các chức vụ
        return self.listChucVu

    def get_chuc_vu(self, index):
        # Trả về chức vụ theo chỉ số trong danh sách
        return self.listChucVu[index]

    def get_chuc_vu_by_mcv(self, mcv):
        # Tìm chức vụ theo MCV
        for index, cv in enumerate(self.listChucVu):
            if cv.MCV == mcv:
                return index
        return -1

    def add_chuc_vu(self, cv):
        # Thêm một chức vụ mới
        ChucVuDAO.insert(cv)

    def update_chuc_vu(self, cv):
        # Cập nhật thông tin chức vụ
        dao = ChucVuDAO()  # Tạo instance của ChucVuDAO
        dao.update(cv)     # Gọi phương thức update thông qua instance

    def delete_chuc_vu(self, mcv):
        # Xóa chức vụ (thực tế là thay đổi trạng thái TT = -1)
        ChucVuDAO.delete(mcv)

    def search(self, txt, type):
        # Tìm kiếm chức vụ theo các tiêu chí
        txt = txt.lower()
        result = []
        if type == "Tất cả":
            result = [cv for cv in self.listChucVu if txt in str(cv.MCV) or txt in cv.TEN.lower()]
        elif type == "Mã chức vụ":
            result = [cv for cv in self.listChucVu if txt in str(cv.MCV)]
        elif type == "Tên chức vụ":
            result = [cv for cv in self.listChucVu if txt in cv.TEN.lower()]
        return result

    def find_chuc_vu_by_ma_chuc_vu(self, ma_chuc_vu):
        # Tìm chức vụ theo MCV
        return ChucVuDAO.select_by_id(ma_chuc_vu)

    def update_muc_luong(self, mcv, new_salary):
        # Cập nhật mức lương của chức vụ
        dao = ChucVuDAO()
        cv = self.find_chuc_vu_by_ma_chuc_vu(mcv)
        if cv:
            cv.MUCLUONG = new_salary
            dao.update(cv)
