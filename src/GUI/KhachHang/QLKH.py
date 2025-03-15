import tkinter as tk
# import customtkinter
from tkinter import messagebox
# from labelForm import create_entry
#


class CustomerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lí khách hàng")
        self.root.geometry("500x400")

        # label
        tk.Label(root, text="Quản lí khách hàng",
                 font=("Arial", 16, "bold")).pack(pady=10)

    # ô nhập
    self.id_input = self.create_entry("ID khách hàng: ")
    self.name_input = self.create_entry("Tên khách hàng: ")
    self.sdt_input = self.create_entry("Số điện thoại: ")
    self.email_input = self.create_entry("Email: ")


if __name__ == "__main__":
    root = tk.Tk()
    app = CustomerApp(root)
    root.mainloop()
