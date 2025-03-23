import sqlite3


def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="customer_db"
    )


def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def insert_sample_data():
    conn = connect_db()
    cursor = conn.cursor()
    sample_data = [
        ("Nguyễn Văn A", "0123456789", "a@gmail.com"),
        ("Trần Thị B", "0987654321", "b@gmail.com"),
        ("Lê Văn C", "0345678901", "c@gmail.com")
    ]
    cursor.executemany(
        "INSERT INTO customers (name, phone, email) VALUES (?, ?, ?)", sample_data)
    conn.commit()
    conn.close()


# Tạo bảng nếu chưa có
create_table()
# Chèn dữ liệu mẫu nếu cần
insert_sample_data()
