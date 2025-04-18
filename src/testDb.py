import mysql.connector

# def test_connection():
#     try:
#         conn = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="",  # Đổi thành mật khẩu MySQL của bạn
#             database="quanlykhachhang",  # Đổi thành tên database của bạn
#             port=3307  # Đổi port nếu cần
#         )
#         if conn.is_connected():
#             print("✅ Kết nối MySQL thành công!")
#         conn.close()
#     except mysql.connector.Error as e:
#         print("❌ Lỗi kết nối:", e)

# test_connection()




def fetch_customers():
    try:
        conn = mysql.connector.connect(
            # host="localhost",
            # user="root",
            # password="",
            # database="quanlykhachhang",
            # port=3307
            
            host="127.0.0.1",
            database="quanlykhachhang",
            user="root",
            password="1234",
            port=3306
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM khachhang LIMIT 5")  # Lấy 5 dòng đầu tiên
        rows = cursor.fetchall()
        
        if rows:
            for row in rows:
                print(row)
        else:
            print("🔍 Không có dữ liệu trong bảng customers.")
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as e:
        print("❌ Lỗi truy vấn:", e)

fetch_customers()