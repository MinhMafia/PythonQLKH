from DAO.GiaoDichDAO import GiaoDichDAO
from DTO.GiaoDichDTO import GiaoDichDTO

class GiaoDichBUS:
    def __init__(self):
        # Lấy danh sách tất cả các giao dịch từ DAO
        self.listGiaoDich = GiaoDichDAO.select_all()

    def get_giao_dich_all(self):
        # Trả về danh sách tất cả giao dịch
        return self.listGiaoDich

    def get_giao_dich(self, index):
        # Trả về giao dịch theo chỉ số trong danh sách
        return self.listGiaoDich[index]

    def get_giao_dich_by_mgd(self, mgd):
        # Tìm giao dịch theo MGD
        for index, gd in enumerate(self.listGiaoDich):
            if gd.MGD == mgd:
                return index
        return -1

    def add_giao_dich(self, gd):
        # Thêm một giao dịch mới
        dao = GiaoDichDAO()  # Tạo instance của GiaoDichDAO
        dao.insert(gd)

    def update_giao_dich(self, gd):
        # Cập nhật thông tin giao dịch
        dao = GiaoDichDAO()  # Tạo instance của GiaoDichDAO
        dao.update(gd)       # Gọi phương thức update thông qua instance

    def delete_giao_dich(self, mgd):
        # Xóa giao dịch (thực tế là thay đổi trạng thái TT = -1)
        GiaoDichDAO.delete(mgd)

    def search(self, txt, type):
        # Tìm kiếm giao dịch theo các tiêu chí
        txt = txt.lower()
        result = []
        if type == "Tất cả":
            result = [gd for gd in self.listGiaoDich if txt in str(gd.MGD) or txt in str(gd.MKH) or txt in str(gd.MNV)]
        elif type == "Mã giao dịch":
            result = [gd for gd in self.listGiaoDich if txt in str(gd.MGD)]
        elif type == "Mã khách hàng":
            result = [gd for gd in self.listGiaoDich if txt in str(gd.MKH)]
        elif type == "Mã nhân viên":
            result = [gd for gd in self.listGiaoDich if txt in str(gd.MNV)]
        return result

    def find_giao_dich_by_ma_giao_dich(self, ma_giao_dich):
        # Tìm giao dịch theo MGD
        return GiaoDichDAO.select_by_id(ma_giao_dich)

    def update_so_tien(self, mgd, new_amount):
        # Cập nhật số tiền giao dịch
        dao = GiaoDichDAO()
        gd = self.find_giao_dich_by_ma_giao_dich(mgd)
        if gd:
            gd.TIEN = new_amount
            dao.update(gd)
    
    def get_max_mgd(self):
        return GiaoDichDAO.get_max_mgd()
    