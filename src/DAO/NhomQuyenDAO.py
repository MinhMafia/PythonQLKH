from DTO.NhomQuyenDTO import NhomQuyenDTO
from config.DatabaseManager import DatabaseManager
from mysql.connector import Error
from DAO.ChiTietQuyenDAO import ChiTietQuyenDAO

class NhomQuyenDAO:
    @staticmethod
    def select_all():
        """Lấy tất cả nhóm quyền từ cơ sở dữ liệu"""
        result = []
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            query = "SELECT * FROM NHOMQUYEN WHERE TT = 1"
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                nhom_quyen = NhomQuyenDTO(
                    MNQ=row["MNQ"],
                    TEN=row["TEN"],
                    TT=row["TT"]
                )
                result.append(nhom_quyen)
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Lỗi khi lấy danh sách nhóm quyền: {e}")
            raise e
        return result

    @staticmethod
    def insert(nhom_quyen_dto):
        """Thêm nhóm quyền mới vào cơ sở dữ liệu và trả về MNQ"""
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor()
            query = "INSERT INTO NHOMQUYEN (TEN, TT) VALUES (%s, %s)"
            params = (nhom_quyen_dto.TEN, nhom_quyen_dto.TT)
            cursor.execute(query, params)
            con.commit()
            mnq = cursor.lastrowid
            print(f"Inserted NhomQuyen, new MNQ: {mnq}")
            DatabaseManager.close_connection(con)
            return mnq
        except Error as e:
            print(f"Lỗi khi thêm nhóm quyền: {e}")
            raise e
        
    @staticmethod
    def update(nhom_quyen_dto):
        """Cập nhật thông tin nhóm quyền"""
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor()
            query = "UPDATE NHOMQUYEN SET TEN = %s, TT = %s WHERE MNQ = %s"
            params = (nhom_quyen_dto.TEN, nhom_quyen_dto.TT, nhom_quyen_dto.MNQ)
            cursor.execute(query, params)
            con.commit()
            DatabaseManager.close_connection(con)
            return True
        except Error as e:
            print(f"Lỗi khi cập nhật nhóm quyền: {e}")
            raise e

    @staticmethod
    def delete(mnq):
        """Xóa nhóm quyền dựa trên mã nhóm quyền"""
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor()
            # Xóa các bản ghi trong CTQUYEN trước
            query_ct = "DELETE FROM CTQUYEN WHERE MNQ = %s"
            cursor.execute(query_ct, (mnq,))
            # Xóa nhóm quyền
            query = "DELETE FROM NHOMQUYEN WHERE MNQ = %s"
            cursor.execute(query, (mnq,))
            con.commit()
            DatabaseManager.close_connection(con)
            return True
        except Error as e:
            print(f"Lỗi khi xóa nhóm quyền: {e}")
            raise e

    @staticmethod
    def select_by_mnq(mnq):
        """Lấy thông tin nhóm quyền dựa trên mã nhóm quyền"""
        result = None
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            query = "SELECT * FROM NHOMQUYEN WHERE MNQ = %s AND TT = 1"
            cursor.execute(query, (mnq,))
            row = cursor.fetchone()
            if row:
                result = NhomQuyenDTO(
                    MNQ=row["MNQ"],
                    TEN=row["TEN"],
                    TT=row["TT"]
                )
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Lỗi khi lấy nhóm quyền theo MNQ: {e}")
            raise e
        return result