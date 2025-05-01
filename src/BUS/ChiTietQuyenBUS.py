from DAO.ChiTietQuyenDAO import ChiTietQuyenDAO
from DTO.ChiTietQuyenDTO import CTQuyenDTO

class CTQuyenBUS:
    def __init__(self):
        self.listCTQuyen = ChiTietQuyenDAO.select_all()

    def get_ct_quyen_all(self):
        return self.listCTQuyen

    def get_ct_quyen(self, index):
        return self.listCTQuyen[index]

    def get_ct_quyen_by_mnq(self, mnq):
        # Lấy trực tiếp từ cơ sở dữ liệu thay vì danh sách
        result = ChiTietQuyenDAO.select_by_mnq(mnq)
        print(f"CTQuyen for MNQ {mnq}: {[ctq.__dict__ for ctq in result]}")
        return result

    def get_ct_quyen_by_mcn(self, mcn):
        return [ctq for ctq in self.listCTQuyen if ctq.MCN == mcn]

    def add_ct_quyen(self, ctq):
        print(f"Adding CTQuyenDTO: {ctq.__dict__}")
        result = ChiTietQuyenDAO.get_instance().insert(ctq)
        if result:
            self.listCTQuyen.append(ctq)
            print(f"Successfully added CTQuyenDTO: {ctq.__dict__}")
        else:
            print(f"Failed to add CTQuyenDTO: {ctq.__dict__}")
        return result

    def update_ct_quyen(self, old_ctq, new_ctq):
        result = ChiTietQuyenDAO.get_instance().update(old_ctq, new_ctq)
        if result:
            self.listCTQuyen.remove(old_ctq)
            self.listCTQuyen.append(new_ctq)
        return result

    def delete_ct_quyen(self, mnq, mcn, hanh_dong):
        ctq = ChiTietQuyenDAO.select_by_id(mnq, mcn, hanh_dong)
        if ctq:
            result = ChiTietQuyenDAO.get_instance().delete(ctq)
            if result:
                self.listCTQuyen.remove(ctq)
            return result
        return False

    def delete_all_by_mnq(self, mnq):
        result = ChiTietQuyenDAO.delete_all_by_mnq(mnq)
        if result:
            self.listCTQuyen[:] = [ctq for ctq in self.listCTQuyen if ctq.MNQ != mnq]
        return result

    def search(self, txt, type):
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