from mysql.connector import Error
from DTO.DanhMucChucNangDTO import DanhMucChucNangDTO
from config.DatabaseManager import DatabaseManager

class DanhMucChucNangDAO:
    @staticmethod
    def select_all():
        """Lấy tất cả danh mục chức năng từ cơ sở dữ liệu"""
        result = []
        try:
            con = DatabaseManager.get_connection()
            cursor = con.cursor(dictionary=True)
            query = "SELECT * FROM DANHMUCCHUCNANG"
            cursor.execute(query)
            for row in cursor.fetchall():
                chuc_nang = DanhMucChucNangDTO(
                    MCN=row["MCN"],
                    TEN=row["TEN"]
                )
                result.append(chuc_nang)
            DatabaseManager.close_connection(con)
        except Error as e:
            print(f"Lỗi khi lấy danh sách danh mục chức năng: {e}")
            raise e
        return result