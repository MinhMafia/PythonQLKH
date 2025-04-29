from mysql.connector import Error
from DTO.GiaoDichDTO import GiaoDichDTO
from config.DatabaseManager import DatabaseManager

class GiaoDichDAO:
    @classmethod
    def get_instance(cls):
        return cls()

    def insert(self, gd: GiaoDichDTO) -> int:
        result = 0
        try:
            con = DatabaseManager.get_connection()
            sql = """INSERT INTO GIAODICH 
                     (MKH, MNV, NGAYGIAODICH, TIEN, TT) 
                     VALUES (%s, %s, %s, %s, %s)"""
            cursor = con.cursor()
            cursor.execute(sql, (gd.MKH, gd.MNV, gd.NGAYGIAODICH, gd.TIEN, gd.TT))
            con.commit()
            result = cursor.rowcount
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    def update(self, gd: GiaoDichDTO) -> int:
        result = 0
        try:
            con = DatabaseManager.get_connection()
            sql = """UPDATE GIAODICH 
                     SET MKH = %s, MNV = %s, NGAYGIAODICH = %s, TIEN = %s, TT = %s 
                     WHERE MGD = %s"""
            cursor = con.cursor()
            cursor.execute(sql, (gd.MKH, gd.MNV, gd.NGAYGIAODICH, gd.TIEN, gd.TT, gd.MGD))
            con.commit()
            result = cursor.rowcount
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    @staticmethod
    def select_all():
        result = []
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT * FROM GIAODICH WHERE TT IN (0, 1, 2)"
            cursor.execute(sql)
            for row in cursor.fetchall():
                gd = GiaoDichDTO(
                    MGD=row["MGD"],
                    MKH=row["MKH"],
                    MNV=row["MNV"],
                    NGAYGIAODICH=row["NGAYGIAODICH"],
                    TIEN=row["TIEN"],
                    TT=row["TT"]
                )
                result.append(gd)
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    def delete(self, mgd):
        result = 0
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor()
            sql = "UPDATE GIAODICH SET TT = -1 WHERE MGD = %s"
            cursor.execute(sql, (mgd,))
            con.commit()
            result = cursor.rowcount
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    @staticmethod
    def select_by_id(mgd):
        result = None
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT * FROM GIAODICH WHERE MGD = %s"
            cursor.execute(sql, (mgd,))
            row = cursor.fetchone()
            if row:
                result = GiaoDichDTO(
                    MGD=row["MGD"],
                    MKH=row["MKH"],
                    MNV=row["MNV"],
                    NGAYGIAODICH=row["NGAYGIAODICH"],
                    TIEN=row["TIEN"],
                    TT=row["TT"]
                )
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    @staticmethod
    def select_by_mkh(mkh):
        result = []
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT * FROM GIAODICH WHERE MKH = %s AND TT IN (0, 1, 2)"
            cursor.execute(sql, (mkh,))
            for row in cursor.fetchall():
                gd = GiaoDichDTO(
                    MGD=row["MGD"],
                    MKH=row["MKH"],
                    MNV=row["MNV"],
                    NGAYGIAODICH=row["NGAYGIAODICH"],
                    TIEN=row["TIEN"],
                    TT=row["TT"]
                )
                result.append(gd)
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result
