# login.py
import customtkinter as ctk
from PIL import Image, ImageTk
import hashlib
from pathlib import Path
from tkinter import messagebox

from BUS.TaiKhoanBUS import TaiKhoanBUS
import component

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

currentDir = Path(__file__).parent
listTaiKhoan = []

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    return TaiKhoanBUS.get_tai_khoan_all()

def fade_transition(root, callback, duration=300, new_geometry=None):
    # Tạo một màn hình chuyển tiếp
    transition_frame = ctk.CTkFrame(root, fg_color="black")
    transition_frame.pack(fill="both", expand=True)

    # Lấy kích thước và vị trí hiện tại của cửa sổ
    root.update_idletasks()
    current_width = root.winfo_width()
    current_height = root.winfo_height()
    current_x = root.winfo_x()
    current_y = root.winfo_y()

    # Nếu có new_geometry, tính toán kích thước và vị trí mục tiêu
    if new_geometry:
        target_width, target_height = map(int, new_geometry.split("x"))
        # Tính vị trí mục tiêu để căn giữa
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        target_x = (screen_width - target_width) // 2
        target_y = (screen_height - target_height) // 2
    else:
        target_width, target_height = current_width, current_height
        target_x, target_y = current_x, current_y

    def fade_in(step=0):
        steps = duration // 30  # Chia thời gian thành các bước (30ms mỗi bước)
        alpha = step / steps
        if step <= steps:
            # Cập nhật màu nền (hiệu ứng mờ dần)
            transition_frame.configure(fg_color=f"#{int(255 * alpha):02x}{int(255 * alpha):02x}{int(255 * alpha):02x}")
            # Tính toán kích thước và vị trí mới
            new_width = int(current_width + (target_width - current_width) * (step / steps))
            new_height = int(current_height + (target_height - current_height) * (step / steps))
            new_x = int(current_x + (target_x - current_x) * (step / steps))
            new_y = int(current_y + (target_y - current_y) * (step / steps))
            # Cập nhật kích thước và vị trí cửa sổ
            root.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
            root.after(30, fade_in, step + 1)
        else:
            transition_frame.destroy()
            # Đảm bảo kích thước và vị trí cuối cùng chính xác
            if new_geometry:
                root.geometry(new_geometry)
                component.CanGiuaCuaSo(root, target_width, target_height)
            callback()

    fade_in()

def login(root):
    TDN = entry_username.get()
    MK = entry_password.get()
    users = load_users()
    check = True
    for user in users:
        if user.TDN == TDN and user.MK == MK:
            check = False
            if user.MNQ == 1:  # Quyền admin
                messagebox.showinfo("Thành công", "Đăng nhập thành công với quyền Admin!")
                fade_transition(root, lambda: import_home_and_run(root), new_geometry="1000x650")
            elif user.MNQ == 2:  # Quyền nhân viên
                messagebox.showinfo("Thành công", "Đăng nhập thành công với quyền Nhân viên!")
                fade_transition(root, lambda: import_staff_home_and_run(root), new_geometry="1000x650")
            return
    if check:
        messagebox.showerror("Lỗi", "Đăng nhập thất bại!")

def import_home_and_run(root):
    import home
    home.homeRun(root)

def import_staff_home_and_run(root):
    import staff_home
    staff_home.staffHomeRun(root)

def open_register_window(root):
    root.withdraw()
    register_window = ctk.CTkToplevel(root)
    register_window.title("Đăng ký")
    register_window.geometry("450x300")
    component.CanGiuaCuaSo(register_window, 450, 300)

    main_frame = ctk.CTkFrame(register_window)
    main_frame.pack(fill="both", expand=True)

    left_frame = ctk.CTkFrame(main_frame, fg_color="#FFD700", width=150)
    right_frame = ctk.CTkFrame(main_frame, fg_color="white")

    left_frame.grid(row=0, column=0, sticky="nsew")
    right_frame.grid(row=0, column=1, sticky="nsew")

    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=2)
    main_frame.grid_rowconfigure(0, weight=1)

    title_label = ctk.CTkLabel(left_frame, text="CHÀO MỪNG", font=("Arial", 18, "bold"), text_color="black")
    title_label.pack(pady=20, expand=True)

    frame = ctk.CTkFrame(right_frame, fg_color="white")
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    ctk.CTkLabel(frame, text="Họ và tên:", text_color="black").pack(anchor="w", pady=2)
    entry_new_name = ctk.CTkEntry(frame, width=200)
    entry_new_name.pack(pady=2)

    ctk.CTkLabel(frame, text="Số điện thoại:", text_color="black").pack(anchor="w", pady=2)
    entry_new_phone = ctk.CTkEntry(frame, width=200)
    entry_new_phone.pack(pady=2)

    ctk.CTkLabel(frame, text="Tên đăng nhập:", text_color="black").pack(anchor="w", pady=2)
    entry_new_username = ctk.CTkEntry(frame, width=200)
    entry_new_username.pack(pady=2)

    ctk.CTkLabel(frame, text="Mật khẩu:", text_color="black").pack(anchor="w", pady=2)
    entry_new_password = ctk.CTkEntry(frame, show="*", width=200)
    entry_new_password.pack(pady=2)

    def register():
        new_name = entry_new_name.get()
        new_phone = entry_new_phone.get()
        new_user = entry_new_username.get()
        new_pass = entry_new_password.get()

        if new_user in [user.TDN for user in load_users()]:
            messagebox.showerror("Lỗi", "Tài khoản đã tồn tại!")
            return
        
        if new_user and new_pass and new_name and new_phone:
            messagebox.showinfo("Thành công", "Đăng ký thành công!")
            register_window.destroy()
            fade_transition(root, lambda: root.deiconify())
        else:
            messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
    
    register_window.grab_set()

    def back_to_login():
        register_window.grab_release()
        register_window.destroy()
        fade_transition(root, lambda: root.deiconify())

    button_frame = ctk.CTkFrame(frame, fg_color="white")
    button_frame.pack(pady=10)

    btn_register = ctk.CTkButton(button_frame, text="Đăng ký", font=("Arial", 12, "bold"), fg_color="#008000", command=register)
    btn_register.grid(row=0, column=0, padx=5)
    btn_back = ctk.CTkButton(button_frame, text="Quay lại", font=("Arial", 12, "bold"), fg_color="#008000", command=back_to_login)
    btn_back.grid(row=0, column=1, padx=5)

def main(root):
    global entry_username, entry_password
    global user_icon, lock_icon

    root.title("Đăng nhập")
    root.geometry("500x250")
    component.CanGiuaCuaSo(root, 500, 250)

    for widget in root.winfo_children():
        widget.destroy()

    main_frame = ctk.CTkFrame(root, fg_color="white")
    main_frame.pack(fill="both", expand=True)

    left_frame = ctk.CTkFrame(main_frame, fg_color="#FFD700", width=150)
    right_frame = ctk.CTkFrame(main_frame, fg_color="white")

    left_frame.grid(row=0, column=0, sticky="nsew")
    right_frame.grid(row=0, column=1, sticky="nsew")

    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=2)
    main_frame.grid_rowconfigure(0, weight=1)

    title_label = ctk.CTkLabel(left_frame, text="WELLCOME TO APP", font=("Arial", 18, "bold"), text_color="white")
    title_label.pack(pady=20, expand=True)

    try:
        userImage_path = currentDir / "img" / "user.png"
        lockImage_path = currentDir / "img" / "lock.jpg"
        if not userImage_path.exists() or not lockImage_path.exists():
            print("Image files not found!")
            return
        user_icon = ctk.CTkImage(light_image=Image.open(userImage_path), size=(25, 20))
        lock_icon = ctk.CTkImage(light_image=Image.open(lockImage_path), size=(25, 20))
    except Exception as e:
        print(f"Error loading images: {e}")
        return

    frame_user = ctk.CTkFrame(right_frame, fg_color="white", border_width=2, corner_radius=5)
    frame_user.pack(pady=10, padx=20, fill="x")
    user_label = ctk.CTkLabel(frame_user, image=user_icon, text="")
    user_label.pack(side="left", padx=5)
    entry_username = ctk.CTkEntry(frame_user, font=("Arial", 12), border_width=0)
    entry_username.pack(side="left", fill="x", expand=True, padx=5)
    entry_username.insert(0, "admin")

    frame_pass = ctk.CTkFrame(right_frame, fg_color="white", border_width=2, corner_radius=5)
    frame_pass.pack(pady=10, padx=20, fill="x")
    pass_label = ctk.CTkLabel(frame_pass, image=lock_icon, text="")
    pass_label.pack(side="left", padx=5)
    entry_password = ctk.CTkEntry(frame_pass, font=("Arial", 12), show="*", border_width=0)
    entry_password.pack(side="left", fill="x", expand=True, padx=5)
    entry_password.insert(0, "123456")

    forgot_label = ctk.CTkLabel(right_frame, text="Quên mật khẩu?", text_color="black", cursor="hand2")
    forgot_label.pack(pady=5)

    btn_login = ctk.CTkButton(right_frame, text="Đăng nhập", font=("Arial", 14, "bold"), fg_color="#FFA500", command=lambda: login(root))
    btn_login.pack(pady=10, padx=50, fill="x")

    register_label = ctk.CTkLabel(right_frame, text="Chưa có tài khoản? Đăng ký ngay", text_color="cyan", cursor="hand2")
    register_label.pack(pady=5)
    register_label.bind("<Button-1>", lambda e: open_register_window(root))

    root.update()

if __name__ == "__main__":
    root = ctk.CTk()
    main(root)
    root.mainloop()