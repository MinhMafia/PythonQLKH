import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
from PIL import Image, ImageTk
import hashlib
import os

import home


FILE_NAME = "src/users.txt"

if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, "w") as f:
        f.write("")


def CanGiuaCuaSo(window, width, height):
    window.resizable(width=False, height=False)
    screen_height = window.winfo_screenheight()
    screen_width = window.winfo_screenwidth()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    users = {}
    with open(FILE_NAME, "r") as f:
        for line in f:
            username, hashed_pw = line.strip().split(":")
            users[username] = hashed_pw
        return users


def save_user(username, password):
    with open(FILE_NAME, "a") as f:
        f.write(f"{username}:{hash_password(password)}\n")


def login():
    username = entry_username.get()
    password = entry_password.get()
    users = load_users()

    if username in users and users[username] == hash_password(password):
        # messagebox.showinfo("Thành công", "Đăng nhập thành công!")

        # root.withdraw()

        home.homeRun(root)
    else:
        messagebox.showerror("Lỗi", "Đăng nhập thất bại!")


def open_register_window():

    root.withdraw()

    register_window = tk.Toplevel(root)
    register_window.title("Đăng ký")
    root.configure(background="#4B0082")
    CanGiuaCuaSo(register_window, 320, 300)

    frame = tk.Frame(register_window)
    frame.pack(padx=10, pady=10, fill="both", expand=True)

    tk.Label(frame, text="Họ và tên:").pack(anchor="w", pady=2)
    entry_new_name = tk.Entry(frame, width=30)
    entry_new_name.pack(pady=2)

    tk.Label(frame, text="Số điện thoại:").pack(anchor="w", pady=2)
    entry_new_phone = tk.Entry(frame, width=30)
    entry_new_phone.pack(pady=2)

    tk.Label(frame, text="Tên đăng nhập:").pack(anchor="w", pady=2)
    entry_new_username = tk.Entry(frame, width=30)
    entry_new_username.pack(pady=2)

    tk.Label(frame, text="Mật khẩu:").pack(anchor="w", pady=2)
    entry_new_password = tk.Entry(frame, show="*", width=30)
    entry_new_password.pack(pady=2)

    def register():
        new_name = entry_new_name.get()
        new_phone = entry_new_phone.get()
        new_user = entry_new_username.get()
        new_pass = entry_new_password.get()

        if new_user in load_users():
            messagebox.showerror("Lỗi", "Tài khoản đã tồn tại!")
            return

        if new_user and new_pass and new_name and new_phone:
            save_user(new_user, new_pass)
            messagebox.showinfo("Thành công", "Đăng ký thành công!")
            register_window.destroy()
            root.deiconify()
        else:
            messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")

    def back_to_login():
        register_window.destroy()
        root.deiconify()

    button_frame = tk.Frame(frame)
    button_frame.pack(pady=10)

    btn_register = tk.Button(button_frame, text="Đăng ký", command=register)
    btn_register.grid(row=0, column=0, padx=5)
    btn_back = tk.Button(button_frame, text="Quay lại", command=back_to_login)
    btn_back.grid(row=0, column=1, padx=5)


root = tk.Tk()
root.title("Đăng nhập")
root.configure(background="#4B0082")
CanGiuaCuaSo(root, 400, 470)


# Logo hoặc tiêu đề
title_label = tk.Label(root, text="Welcome to App", font=(
    "Arial", 18, "bold"), fg="white", bg="#4B0082")
title_label.pack(pady=20)


user_icon = ImageTk.PhotoImage(Image.open(
    "src/images/user.png").resize((20, 20)))
lock_icon = ImageTk.PhotoImage(Image.open(
    "src/images/lock.jpg").resize((20, 20)))


frame_user = tk.Frame(root, bg="white", bd=2, relief="groove")
frame_user.pack(pady=10, padx=20, fill="x")
user_label = tk.Label(frame_user, image=user_icon, bg="white")
user_label.pack(side="left", padx=5)
entry_username = tk.Entry(frame_user, font=("Arial", 12), bd=0)
entry_username.pack(side="left", fill="x", expand=True)


frame_pass = tk.Frame(root, bg="white", bd=2, relief="groove")
frame_pass.pack(pady=10, padx=20, fill="x")
pass_label = tk.Label(frame_pass, image=lock_icon, bg="white")
pass_label.pack(side="left", padx=5)
entry_password = tk.Entry(frame_pass, font=("Arial", 12), show="*", bd=0)
entry_password.pack(side="left", fill="x", expand=True)


forgot_label = tk.Label(root, text="Quên mật khẩu?",
                        fg="yellow", bg="#4B0082", cursor="hand2")
forgot_label.pack(pady=5)


btn_login = tk.Button(root, text="Đăng nhập", font=(
    "Arial", 14, "bold"), bg="#FFA500", fg="white", command=login)
btn_login.pack(pady=10, padx=50, fill="x")


register_label = tk.Label(
    root, text="Chưa có tài khoản? Đăng ký ngay", fg="cyan", bg="#4B0082", cursor="hand2")
register_label.pack(pady=5)
register_label.bind("<Button-1>", lambda e: open_register_window())

root.mainloop()
