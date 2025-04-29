from mysql.connector import Error
from DTO.ChucVuDTO import ChucVuDTO
from config.DatabaseManager import DatabaseManager

class ChucVuDAO:
    @classmethod
    def get_instance(cls):
        return cls()

    def insert(self, cv: ChucVuDTO) -> int:
        result = 0
        try:
            con = DatabaseManager.get_connection()
            sql = """INSERT INTO CHUCVU 
                     (TEN, MUCLUONG, TT) 
                     VALUES (%s, %s, %s)"""
            cursor = con.cursor()
            cursor.execute(sql, (cv.TEN, cv.MUCLUONG, cv.TT))
            con.commit()
            result = cursor.rowcount
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    def update(self, cv: ChucVuDTO) -> int:
        result = 0
        try:
            con = DatabaseManager.get_connection()
            sql = """UPDATE CHUCVU 
                     SET TEN = %s, MUCLUONG = %s, TT = %s 
                     WHERE MCV = %s"""
            cursor = con.cursor()
            cursor.execute(sql, (cv.TEN, cv.MUCLUONG, cv.TT, cv.MCV))
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
            sql = "SELECT * FROM CHUCVU WHERE TT IN (0, 1, 2)"
            cursor.execute(sql)
            for row in cursor.fetchall():
                cv = ChucVuDTO(
                    MCV=row["MCV"],
                    TEN=row["TEN"],
                    MUCLUONG=row["MUCLUONG"],
                    TT=row["TT"]
                )
                result.append(cv)
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    def delete(self, mcv):
        result = 0
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor()
            sql = "UPDATE CHUCVU SET TT = -1 WHERE MCV = %s"
            cursor.execute(sql, (mcv,))
            con.commit()
            result = cursor.rowcount
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    @staticmethod
    def select_by_id(mcv):
        result = None
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT * FROM CHUCVU WHERE MCV = %s"
            cursor.execute(sql, (mcv,))
            row = cursor.fetchone()
            if row:
                result = ChucVuDTO(
                    MCV=row["MCV"],
                    TEN=row["TEN"],
                    MUCLUONG=row["MUCLUONG"],
                    TT=row["TT"]
                )
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result
