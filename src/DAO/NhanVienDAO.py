from mysql.connector import Error
from DTO.NhanVienDTO import NhanVienDTO
from config.DatabaseManager import DatabaseManager

class NhanVienDAO:
    @classmethod
    def get_instance(cls):
        return cls()

    def insert(self, nv: NhanVienDTO) -> int:
        result = 0
        try:
            con = DatabaseManager.get_connection()
            sql = "INSERT INTO NHANVIEN (HOTEN, GIOITINH, NGAYSINH, SDT, EMAIL, MCV, TT) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor = con.cursor()
            cursor.execute(sql, (nv.HOTEN, nv.GIOITINH, nv.NGAYSINH, nv.SDT, nv.EMAIL, nv.MCV, nv.TT))
            con.commit()
            result = cursor.rowcount
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    def update(self, nv: NhanVienDTO) -> int:
        result = 0
        try:
            con = DatabaseManager.get_connection()
            sql = "UPDATE NHANVIEN SET HOTEN = %s, GIOITINH = %s, NGAYSINH = %s, SDT = %s, EMAIL = %s, MCV = %s, TT = %s WHERE MNV = %s"
            cursor = con.cursor()
            cursor.execute(sql, (nv.HOTEN, nv.GIOITINH, nv.NGAYSINH, nv.SDT, nv.EMAIL, nv.MCV, nv.TT, nv.MNV))
            con.commit()
            result = cursor.rowcount
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    def select_all(self):
        result = []
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT * FROM NHANVIEN WHERE TT IN (0, 1, 2)"
            cursor.execute(sql)
            for row in cursor.fetchall():
                nv = NhanVienDTO(
                    MNV=row["MNV"],
                    HOTEN=row["HOTEN"],
                    GIOITINH=row["GIOITINH"],
                    NGAYSINH=row["NGAYSINH"],
                    SDT=row["SDT"],
                    EMAIL=row["EMAIL"],
                    MCV=row["MCV"],
                    TT=row["TT"]
                )
                result.append(nv)
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    def delete(self, mnv):
        result = 0
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor()
            sql = "UPDATE NHANVIEN SET TT = -1 WHERE MNV = %s"
            cursor.execute(sql, (mnv,))
            con.commit()
            result = cursor.rowcount
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    @staticmethod
    def select_by_id(mnv):
        result = None
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT * FROM NHANVIEN WHERE MNV = %s"
            cursor.execute(sql, (mnv,))
            row = cursor.fetchone()
            if row:
                result = NhanVienDTO(
                    MNV=row["MNV"],
                    HOTEN=row["HOTEN"],
                    GIOITINH=row["GIOITINH"],
                    NGAYSINH=row["NGAYSINH"],
                    SDT=row["SDT"],
                    EMAIL=row["EMAIL"],
                    MCV=row["MCV"],
                    TT=row["TT"]
                )
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    @staticmethod
    def select_by_email(email):
        result = None
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT * FROM NHANVIEN WHERE EMAIL = %s"
            cursor.execute(sql, (email,))
            row = cursor.fetchone()
            if row:
                result = NhanVienDTO(
                    MNV=row["MNV"],
                    HOTEN=row["HOTEN"],
                    GIOITINH=row["GIOITINH"],
                    NGAYSINH=row["NGAYSINH"],
                    SDT=row["SDT"],
                    EMAIL=row["EMAIL"],
                    MCV=row["MCV"],
                    TT=row["TT"]
                )
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    def is_account_inactive(self, email):
        is_inactive = False
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT TT FROM NHANVIEN WHERE EMAIL = %s"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
            if result and result["TT"] == -1:
                is_inactive = True
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return is_inactive
