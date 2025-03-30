from mysql.connector import Error
from DTO.KhanhHangDTO import KhachHangDTO
from config.DatabaseManager import DatabaseManager

class KhachHangDAO:
    @classmethod
    def get_instance(cls):
        return cls()

    def insert(self, kh: KhachHangDTO) -> int:
        result = 0
        try:
            con = DatabaseManager.get_connection()
            sql = "INSERT INTO KHACHHANG (MKH, HOTEN, NGAYTHAMGIA, DIACHI, SDT, EMAIL, TT) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor = con.cursor()
            cursor.execute(sql, (kh.MKH, kh.HOTEN, kh.NGAYTHAMGIA, kh.DIACHI, kh.SDT, kh.EMAIL, kh.TT))
            con.commit()
            result = cursor.rowcount
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    def update(self, kh: KhachHangDTO) -> int:
        result = 0
        try:
            con = DatabaseManager.get_connection()
            sql = "UPDATE KHACHHANG SET HOTEN = %s, DIACHI = %s, SDT = %s, EMAIL = %s, TT = %s WHERE MKH = %s"
            cursor = con.cursor()
            cursor.execute(sql, (kh.HOTEN, kh.DIACHI, kh.SDT, kh.EMAIL, kh.TT, kh.MKH))
            con.commit()
            result = cursor.rowcount
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    def select_all():
        result = []
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT * FROM KHACHHANG WHERE TT IN (0, 1, 2)"
            cursor.execute(sql)
            for row in cursor.fetchall():
                kh = KhachHangDTO(
                    MKH=row["MKH"],
                    HOTEN=row["HOTEN"],
                    NGAYTHAMGIA=row["NGAYTHAMGIA"],
                    DIACHI=row["DIACHI"],
                    SDT=row["SDT"],
                    EMAIL=row["EMAIL"],
                    TT=row["TT"]
                )
                result.append(kh)
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result
    
    def delete(self, mkh):
        result = 0
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor()
            sql = "UPDATE KHACHHANG SET TT = -1 WHERE MKH = %s"
            cursor.execute(sql, (mkh,))
            con.commit()
            result = cursor.rowcount
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    @staticmethod
    def select_by_id(mkh):
        result = None
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT * FROM KHACHHANG WHERE MKH = %s"
            cursor.execute(sql, (mkh,))
            row = cursor.fetchone()
            if row:
                result = KhachHangDTO(row["MKH"], row["HOTEN"], row["NGAYTHAMGIA"], row["DIACHI"], row["SDT"], row["EMAIL"], row["TT"])
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
            sql = "SELECT * FROM KHACHHANG WHERE EMAIL = %s"
            cursor.execute(sql, (email,))
            row = cursor.fetchone()
            if row:
                result = KhachHangDTO(row["MKH"], row["HOTEN"], row["NGAYTHAMGIA"], row["DIACHI"], row["SDT"], row["EMAIL"], row["TT"])
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result
    
    def is_account_inactive(self, email):
        is_inactive = False
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT TT FROM KHACHHANG WHERE EMAIL = %s"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
            if result and result["TT"] == -1:
                is_inactive = True
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return is_inactive
