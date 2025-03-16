import customtkinter as ctk

root = ctk.CTk()
root.title = "Đăng nhập"
root.geometry("400x300")

label = ctk.CTkLabel(root, text="Đăng nhập", font=("Arial", 20)).pack(pady=20)

user_name = ctk.CTkEntry(root, placeholder_text="Tài khoản")
user_name.pack(pady=10)

pass_Word = ctk.CTkEntry(root, placeholder_text="Mật khẩu", show="*")
pass_Word.pack(pady=10)


def login():
    print("Đăng nhập với username:", user_name.get())


login_Btn = ctk.CTkButton(root, text="Đăng nhập", command=login).pack(pady=30)

root.mainloop()
