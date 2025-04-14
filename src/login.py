import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
from PIL import Image, ImageTk
import hashlib
import os
from pathlib import Path

from BUS.TaiKhoanBUS import TaiKhoanBUS

import home
import component

# Đường dẫn thư mục hiện tại
currentDir = Path(__file__).parent

listTaiKhoan = []

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    return TaiKhoanBUS.get_tai_khoan_all()

# def save_user(username, password):
#     TaiKhoanBUS.add_acc()

def login():
    TDN = entry_username.get()
    MK = entry_password.get()
    users = load_users()
    check = True
    for user in users:
        if user.TDN == TDN and user.MK == MK:
            # messagebox.showinfo("Thành công", "Đăng nhập thành công!")
            check = False
            home.homeRun(root)
    if check:
        messagebox.showerror("Lỗi", "Đăng nhập thất bại!")
            
        
def open_register_window():

    root.withdraw()

    register_window = tk.Toplevel(root)
    register_window.title("Đăng ký")
    root.configure(background="#4B0082")
    component.CanGiuaCuaSo(register_window, 450, 300)
    main_frame = tk.Frame(register_window, bg="white")
    main_frame.pack(fill="both", expand=True)



    left_frame = tk.Frame(main_frame, bg="#FFD700", width=300, height=500)
    right_frame = tk.Frame(main_frame, bg="white", width=500, height=500)

    left_frame.grid(row=0, column=0, sticky="nsew")
    right_frame.grid(row=0, column=1, sticky="nsew")

    right_frame.grid_columnconfigure(0, weight=1)
    right_frame.grid_columnconfigure(1, weight=2)
    right_frame.grid_rowconfigure(0, weight=1)

    title_label = tk.Label(left_frame, text="CHÀO MỪNG", font=("Arial", 18, "bold"), fg="black", bg="#FFD700")
    title_label.pack(pady=20, expand=True)

    frame = tk.Frame(right_frame, bg="white")
    frame.pack(pady=20, padx=20, fill="both", expand=True)

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
    
    # Khóa tương tác cửa sổ khác
    register_window.grab_set()

    def back_to_login():
        register_window.grab_release()
        register_window.destroy()
        root.deiconify()

    button_frame = tk.Frame(frame, bg="white")
    button_frame.pack(pady=10)

    btn_register = tk.Button(button_frame, text="Đăng ký", font=("Arial", 12, "bold"), bg="#008000", fg="white", command=register)
    btn_register.grid(row=0, column=0, padx=5)
    btn_back = tk.Button(button_frame, text="Quay lại",font=("Arial", 12, "bold"), bg="#008000", fg="white", command=back_to_login)
    btn_back.grid(row=0, column=1, padx=5)

root = tk.Tk()
root.title("Đăng nhập")
root.configure(background="white")
component.CanGiuaCuaSo(root, 500, 250)

main_frame = tk.Frame(root, bg="white")
main_frame.pack(fill="both", expand=True)

left_frame = tk.Frame(main_frame, bg="#FFD700", width=300, height=500)
right_frame = tk.Frame(main_frame, bg="white", width=500, height=500)

left_frame.grid(row=0, column=0, sticky="nsew")
right_frame.grid(row=0, column=1, sticky="nsew")

right_frame.grid_columnconfigure(0, weight=1)
right_frame.grid_columnconfigure(1, weight=2)
right_frame.grid_rowconfigure(0, weight=1)

# Logo hoặc tiêu đề
title_label = tk.Label(left_frame, text="WELLCOME TO APP", font=("Arial", 18, "bold"), fg="white", bg="#FFD700")
title_label.pack(pady=20, expand=True)

userImage_path = currentDir / "img" / "user.png"
user_icon = ImageTk.PhotoImage(Image.open(userImage_path).resize((25, 20)))
lockImage_path = currentDir / "img" / "lock.jpg"
lock_icon = ImageTk.PhotoImage(Image.open(lockImage_path).resize((25, 20)))



frame_user = tk.Frame(right_frame, bg="white", bd=2, relief="groove")
frame_user.pack(pady=10, padx=20, fill="x")
user_label = tk.Label(frame_user, image=user_icon, bg="white")
user_label.pack(side="left", padx=5)
entry_username = tk.Entry(frame_user, font=("Arial", 12), bd=0)
entry_username.pack(side="left", fill="x", expand=True)
entry_username.insert(0, "admin")


frame_pass = tk.Frame(right_frame, bg="white", bd=2, relief="groove")
frame_pass.pack(pady=10, padx=20, fill="x")
pass_label = tk.Label(frame_pass, image=lock_icon, bg="white")
pass_label.pack(side="left", padx=5)
entry_password = tk.Entry(frame_pass, font=("Arial", 12), show="*", bd=0)
entry_password.pack(side="left", fill="x", expand=True)
entry_password.insert(0, "123456")


forgot_label = tk.Label(right_frame, text="Quên mật khẩu?", fg="black", bg="white", cursor="hand2")
forgot_label.pack(pady=5)


btn_login = tk.Button(right_frame, text="Đăng nhập", font=("Arial", 14, "bold"), bg="#FFA500", fg="white", command=login)
btn_login.pack(pady=10, padx=50, fill="x")


register_label = tk.Label(right_frame, text="Chưa có tài khoản? Đăng ký ngay", fg="cyan", bg="white", cursor="hand2")
register_label.pack(pady=5)
register_label.bind("<Button-1>", lambda e: open_register_window())

root.mainloop()

