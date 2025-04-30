from mysql.connector import Error
from DTO.KhachHangDTO import KhachHangDTO  # Sửa import
from config.DatabaseManager import DatabaseManager

class KhachHangDAO:
    @classmethod
    def get_instance(cls):
        return cls()

    def insert(self, kh: KhachHangDTO) -> int:
        result = 0
        try:
            con = DatabaseManager.get_connection()
            sql = """INSERT INTO KHACHHANG 
                     (HOTEN, NGAYTHAMGIA, DIACHI, SDT, EMAIL, CCCD, TIEN, TT) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor = con.cursor()
            cursor.execute(sql, (kh.HOTEN, kh.NGAYTHAMGIA, kh.DIACHI, kh.SDT, kh.EMAIL, kh.CCCD, kh.TIEN, kh.TT))
            con.commit()
            result = cursor.rowcount
            # print(f"insert customer: {kh.__dict__}, rowcount={result}")  # Log
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error in insert: {e}")
            raise e
        return result

    def update(self, kh: KhachHangDTO) -> int:
        result = 0
        try:
            con = DatabaseManager.get_connection()
            sql = """UPDATE KHACHHANG 
                     SET HOTEN = %s, DIACHI = %s, SDT = %s, EMAIL = %s, CCCD = %s, TIEN = %s, TT = %s 
                     WHERE MKH = %s"""
            cursor = con.cursor()
            cursor.execute(sql, (kh.HOTEN, kh.DIACHI, kh.SDT, kh.EMAIL, kh.CCCD, kh.TIEN, kh.TT, kh.MKH))
            con.commit()
            result = cursor.rowcount
            # print(f"update customer MKH={kh.MKH}, rowcount={result}")  # Log
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error in update: {e}")
            raise e
        return result

    @staticmethod
    def select_all():
        result = []
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT * FROM KHACHHANG WHERE TT IN (0, 1, 2)"
            # print("Executing select_all query:", sql)  # Log truy vấn
            cursor.execute(sql)
            rows = cursor.fetchall()
            # print("select_all rows:", rows)  # Log dữ liệu thô
            for row in rows:
                kh = KhachHangDTO(
                    MKH=row["MKH"],
                    HOTEN=row["HOTEN"],
                    NGAYTHAMGIA=row["NGAYTHAMGIA"],
                    DIACHI=row["DIACHI"],
                    SDT=row["SDT"],
                    EMAIL=row["EMAIL"],
                    CCCD=row["CCCD"],
                    TIEN=row["TIEN"],
                    TT=row["TT"]
                )
                result.append(kh)
            # print("select_all result:", [r.__dict__ for r in result])  # Log đối tượng DTO
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error in select_all: {e}")
            raise e  # Ném lại ngoại lệ
        return result

    @staticmethod
    def select_by_cccd(cccd):
        result = None
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT * FROM KHACHHANG WHERE CCCD = %s"
            cursor.execute(sql, (cccd,))
            row = cursor.fetchone()
            # print(f"select_by_cccd CCCD={cccd}, row={row}")  # Log
            if row:
                result = KhachHangDTO(
                    MKH=row["MKH"],
                    HOTEN=row["HOTEN"],
                    NGAYTHAMGIA=row["NGAYTHAMGIA"],
                    DIACHI=row["DIACHI"],
                    SDT=row["SDT"],
                    EMAIL=row["EMAIL"],
                    CCCD=row["CCCD"],
                    TIEN=row["TIEN"],
                    TT=row["TT"]
                )
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error in select_by_cccd: {e}")
            raise e
        return result

    def delete(self, mkh):
        result = 0
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor()
            sql = "UPDATE KHACHHANG SET TT = 0 WHERE MKH = %s"
            cursor.execute(sql, (mkh,))
            con.commit()
            result = cursor.rowcount
            # print(f"delete customer MKH={mkh}, rowcount={result}")  # Log
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error in delete: {e}")
            raise e
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
            # print(f"select_by_id MKH={mkh}, row={row}")  # Log
            if row:
                result = KhachHangDTO(
                    MKH=row["MKH"],
                    HOTEN=row["HOTEN"],
                    NGAYTHAMGIA=row["NGAYTHAMGIA"],
                    DIACHI=row["DIACHI"],
                    SDT=row["SDT"],
                    EMAIL=row["EMAIL"],
                    CCCD=row["CCCD"],
                    TIEN=row["TIEN"],
                    TT=row["TT"]
                )
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error in select_by_id: {e}")
            raise e
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
            # print(f"select_by_email email={email}, row={row}")  # Log
            if row:
                result = KhachHangDTO(
                    MKH=row["MKH"],
                    HOTEN=row["HOTEN"],
                    NGAYTHAMGIA=row["NGAYTHAMGIA"],
                    DIACHI=row["DIACHI"],
                    SDT=row["SDT"],
                    EMAIL=row["EMAIL"],
                    CCCD=row["CCCD"],
                    TIEN=row["TIEN"],
                    TT=row["TT"]
                )
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error in select_by_email: {e}")
            raise e
        return result

    def is_account_inactive(self, email):
        is_inactive = False
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT TT FROM KHACHHANG WHERE EMAIL = %s"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
            # print(f"is_account_inactive email={email}, result={result}")  # Log
            if result and result["TT"] == 0:
                is_inactive = True
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error in is_account_inactive: {e}")
            raise e
        return is_inactive

    def update_email_by_makh(self, mkh, email):  # Thêm phương thức bị thiếu
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor()
            sql = "UPDATE KHACHHANG SET EMAIL = %s WHERE MKH = %s"
            cursor.execute(sql, (email, mkh))
            con.commit()
            # print(f"update_email_by_makh MKH={mkh}, email={email}, rowcount={cursor.rowcount}")  # Log
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error in update_email_by_makh: {e}")
            raise e