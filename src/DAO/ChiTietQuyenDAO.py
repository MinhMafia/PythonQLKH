from mysql.connector import Error
from DTO.ChiTietQuyenDTO import ChiTietQuyenDTO
from config.DatabaseManager import DatabaseManager

class ChiTietQuyenDAO:
    @classmethod
    def get_instance(cls):
        return cls()

    def insert(self, ctq: ChiTietQuyenDTO) -> int:
        result = 0
        try:
            con = DatabaseManager.get_connection()
            sql = """INSERT INTO CTQUYEN 
                     (MNQ, MCN, HANHDONG) 
                     VALUES (%s, %s, %s)"""
            cursor = con.cursor()
            cursor.execute(sql, (ctq.MNQ, ctq.MCN, ctq.HANHDONG))
            con.commit()
            result = cursor.rowcount
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    def update(self, old_ctq: ChiTietQuyenDTO, new_ctq: ChiTietQuyenDTO) -> int:
        """
        Cập nhật bản ghi CTQUYEN dựa trên khóa chính cũ (MNQ, MCN, HANHDONG)
        """
        result = 0
        try:
            con = DatabaseManager.get_connection()
            sql = """UPDATE CTQUYEN 
                     SET MNQ = %s, MCN = %s, HANHDONG = %s 
                     WHERE MNQ = %s AND MCN = %s AND HANHDONG = %s"""
            cursor = con.cursor()
            cursor.execute(sql, (
                new_ctq.MNQ, new_ctq.MCN, new_ctq.HANHDONG,
                old_ctq.MNQ, old_ctq.MCN, old_ctq.HANHDONG
            ))
            con.commit()
            result = cursor.rowcount
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    def delete(self, ctq: ChiTietQuyenDTO) -> int:
        result = 0
        try:
            con = DatabaseManager.get_connection()
            sql = "DELETE FROM CTQUYEN WHERE MNQ = %s AND MCN = %s AND HANHDONG = %s"
            cursor = con.cursor()
            cursor.execute(sql, (ctq.MNQ, ctq.MCN, ctq.HANHDONG))
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
            sql = "SELECT * FROM CTQUYEN"
            cursor.execute(sql)
            for row in cursor.fetchall():
                ctq = ChiTietQuyenDTO(
                    MNQ=row["MNQ"],
                    MCN=row["MCN"],
                    HANHDONG=row["HANHDONG"]
                )
                result.append(ctq)
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result

    @staticmethod
    def select_by_id(mnq: int, mcn: str, hanhdong: str):
        result = None
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            sql = "SELECT * FROM CTQUYEN WHERE MNQ = %s AND MCN = %s AND HANHDONG = %s"
            cursor.execute(sql, (mnq, mcn, hanhdong))
            row = cursor.fetchone()
            if row:
                result = ChiTietQuyenDTO(
                    MNQ=row["MNQ"],
                    MCN=row["MCN"],
                    HANHDONG=row["HANHDONG"]
                )
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Error: {e}")
        return result
