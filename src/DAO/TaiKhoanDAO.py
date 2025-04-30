from mysql.connector import Error
from DTO.TaiKhoanDTO import TaiKhoanDTO
from config.DatabaseManager import DatabaseManager

class TaiKhoanDAO:
    @classmethod
    def get_instance(cls):
        return cls()

    def insert(self, t: TaiKhoanDTO) -> int:
        result = 0
        try:
            con = DatabaseManager.get_connection()
            sql = "INSERT INTO TAIKHOAN (MNV, TDN, MK, MNQ, TT) VALUES (%s, %s, %s, %s, %s)"
            cursor = con.cursor()
            print(f"TaiKhoanDAO: Executing SQL - MNV: {t.MNV}, TDN: {t.TDN}, MK: {t.MK}, MNQ: {t.MNQ}, TT: {t.TT}")
            cursor.execute(sql, (t.MNV, t.TDN, t.MK, t.MNQ, t.TT))
            con.commit()
            result = cursor.rowcount
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error inserting account: {e}")
            raise e  # Ném lại lỗi để hiển thị trong TaiKhoan.py
        return result

    def update(self, t: TaiKhoanDTO) -> int:
        result = 0
        try:
            con = DatabaseManager.get_connection()
            sql = "UPDATE TAIKHOAN SET TDN = %s, TT = %s, MNQ = %s WHERE MNV = %s"
            cursor = con.cursor()
            cursor.execute(sql, (t.TDN, t.TT, t.MNQ, t.MNV))
            con.commit()
            result = cursor.rowcount
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
            raise e
        return result

    def update_tt_cxl(self, email: str) -> int:
        result = 0
        try:
            con = DatabaseManager.get_connection()
            sql = "UPDATE TAIKHOAN TK JOIN NHANVIEN NV ON TK.MNV = NV.MNV SET TK.TT = 2 WHERE NV.EMAIL = %s"
            cursor = con.cursor()
            cursor.execute(sql, (email,))
            con.commit()
            result = cursor.rowcount
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
            raise e
        return result

    def update_pass(self, email: str, password: str):
        result = 0
        try:
            con = DatabaseManager.get_connection()
            sql = "UPDATE TAIKHOAN TK JOIN NHANVIEN NV ON TK.MNV = NV.MNV SET TK.MK = %s WHERE NV.EMAIL = %s"
            cursor = con.cursor()
            cursor.execute(sql, (password, email))
            con.commit()
            result = cursor.rowcount  # Số dòng bị ảnh hưởng
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error updating password: {e}")
            raise e
        return result

    def select_all():
        result = []
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT * FROM taikhoan WHERE TT IN (0, 1, 2)"
            cursor.execute(sql)
            for row in cursor.fetchall():
                tk = TaiKhoanDTO(
                    MNV=row["MNV"],
                    TDN=row["TDN"],
                    MK=row["MK"],
                    MNQ=row["MNQ"],
                    TT=row["TT"]
                )
                result.append(tk)
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
            raise e
        return result
    
    def delete(self, mnv):
        result = 0
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor()
            sql = "UPDATE TAIKHOAN SET TT = -1 WHERE MNV = %s"
            cursor.execute(sql, (mnv,))
            con.commit()
            result = cursor.rowcount  # Số dòng bị ảnh hưởng
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
            raise e
        return result

    @staticmethod
    def select_by_id(mnv):
        result = None
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT * FROM TAIKHOAN WHERE MNV = %s"
            cursor.execute(sql, (mnv,))
            row = cursor.fetchone()
            if row:
                result = TaiKhoanDTO(row["MNV"], row["TDN"], row["MK"], row["MNQ"], row["TT"])
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
            raise e
        return result

    @staticmethod
    def select_by_user(tdn):
        result = None
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT * FROM TAIKHOAN WHERE TDN = %s"
            cursor.execute(sql, (tdn,))
            row = cursor.fetchone()
            if row:
                result = TaiKhoanDTO(row["MNV"], row["TDN"], row["MK"], row["MNQ"], row["TT"])
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
            raise e
        return result
    
    def is_account_inactive(self, username):
        is_inactive = False
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT TT FROM TAIKHOAN WHERE TDN = %s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            if result and result["TT"] == -1:
                is_inactive = True
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
            raise e
        return is_inactive