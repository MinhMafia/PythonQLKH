import mysql.connector
from mysql.connector import Error

class DatabaseManager:
    @staticmethod
    def get_connection():
        connection = None
        try:
            connection = mysql.connector.connect(
                host="localhost",
                database="quanlykhachhang",
                user="root",
                password="",
                port=3307
            )
            if connection.is_connected():
                print("Kết nối thành công đến cơ sở dữ liệu!")
        except Error as e:
            print("Không thể kết nối đến cơ sở dữ liệu!", e)
        return connection

    @staticmethod
    def close_connection(connection):
        if connection is not None and connection.is_connected():
            connection.close()
            print("Kết nối đã được đóng.")
