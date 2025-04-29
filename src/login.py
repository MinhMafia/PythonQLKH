import customtkinter as ctk
from PIL import Image, ImageTk
import hashlib
from pathlib import Path
from tkinter import messagebox
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

from BUS.TaiKhoanBUS import TaiKhoanBUS
from BUS.NhanVienBUS import NhanVienBUS
import component

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

currentDir = Path(__file__).parent
listTaiKhoan = []

# Tùy chọn gửi email hoặc hiển thị OTP qua messagebox
USE_EMAIL = False  # Đặt thành True để thử gửi email, False để hiển thị OTP qua messagebox

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    return TaiKhoanBUS.get_tai_khoan_all()

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def is_valid_email(email):
    # Kiểm tra định dạng email cơ bản
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def send_otp_email(receiver_email, otp):
    # Cấu hình thông tin gửi email
    sender_email = "your_real_gmail@gmail.com"  # Thay bằng email của bạn
    sender_password = "yfaqmothhtzeciwd"  # Thay bằng mật khẩu ứng dụng của Gmail
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Kiểm tra định dạng email người nhận
    if not is_valid_email(receiver_email):
        print(f"Invalid email format: {receiver_email}")
        messagebox.showerror("Lỗi", f"Email người nhận không hợp lệ: {receiver_email}")
        return False

    # Tạo nội dung email
    subject = "Mã OTP để đặt lại mật khẩu"
    body = f"Mã OTP của bạn là: {otp}\nVui lòng sử dụng mã này để đặt lại mật khẩu."
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Gửi email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print(f"OTP sent successfully to {receiver_email}")
        return True
    except smtplib.SMTPAuthenticationError as auth_error:
        print(f"Authentication error: {auth_error}")
        messagebox.showerror("Lỗi", "Thông tin đăng nhập SMTP không đúng. Vui lòng kiểm tra email và mật khẩu ứng dụng!\nChi tiết lỗi: " + str(auth_error))
        return False
    except smtplib.SMTPRecipientsRefused as recip_error:
        print(f"Recipient error: {recip_error}")
        messagebox.showerror("Lỗi", f"Không thể gửi email đến {receiver_email}. Email không tồn tại hoặc bị từ chối!\nChi tiết lỗi: {recip_error}")
        return False
    except Exception as e:
        print(f"Error sending email: {e}")
        messagebox.showerror("Lỗi", f"Không thể gửi mã OTP qua email: {e}")
        return False

def fade_transition(root, callback, duration=300, new_geometry=None):
    transition_frame = ctk.CTkFrame(root, fg_color="black")
    transition_frame.pack(fill="both", expand=True)

    root.update_idletasks()
    current_width = root.winfo_width()
    current_height = root.winfo_height()
    current_x = root.winfo_x()
    current_y = root.winfo_y()

    if new_geometry:
        target_width, target_height = map(int, new_geometry.split("x"))
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        target_x = (screen_width - target_width) // 2
        target_y = (screen_height - target_height) // 2
    else:
        target_width, target_height = current_width, current_height
        target_x, target_y = current_x, current_y

    def fade_in(step=0):
        steps = duration // 30
        alpha = step / steps
        if step <= steps:
            transition_frame.configure(fg_color=f"#{int(255 * alpha):02x}{int(255 * alpha):02x}{int(255 * alpha):02x}")
            new_width = int(current_width + (target_width - current_width) * (step / steps))
            new_height = int(current_height + (target_height - current_height) * (step / steps))
            new_x = int(current_x + (target_x - current_x) * (step / steps))
            new_y = int(current_y + (target_y - current_y) * (step / steps))
            root.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
            root.after(30, fade_in, step + 1)
        else:
            transition_frame.destroy()
            if new_geometry:
                root.geometry(new_geometry)
                component.CanGiuaCuaSo(root, target_width, target_height)
            callback()

    fade_in()

def login(root):
    TDN = entry_username.get()
    MK = hash_password(entry_password.get())
    users = load_users()
    check = True
    for user in users:
        if user.TDN == TDN and user.MK == MK:
            check = False
            if user.MNQ == 1:
                messagebox.showinfo("Thành công", "Đăng nhập thành công với quyền Admin!")
                fade_transition(root, lambda: import_home_and_run(root), new_geometry="1000x650")
            elif user.MNQ == 2:
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

def open_forgot_password_window(root):
    root.withdraw()
    forgot_window = ctk.CTkToplevel(root)
    forgot_window.title("Quên mật khẩu")
    forgot_window.geometry("700x300")
    component.CanGiuaCuaSo(forgot_window, 700, 300)

    main_frame = ctk.CTkFrame(forgot_window)
    main_frame.pack(fill="both", expand=True)

    left_frame = ctk.CTkFrame(main_frame, fg_color="#FFD700", width=150)
    right_frame = ctk.CTkFrame(main_frame, fg_color="white")

    left_frame.grid(row=0, column=0, sticky="nsew")
    right_frame.grid(row=0, column=1, sticky="nsew")

    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=2)
    main_frame.grid_rowconfigure(0, weight=1)

    title_label = ctk.CTkLabel(left_frame, text="QUÊN MẬT KHẨU", font=("Arial", 18, "bold"), text_color="black")
    title_label.pack(pady=20, expand=True)

    frame = ctk.CTkFrame(right_frame, fg_color="white")
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    temp_otp = None
    temp_username = None
    temp_email = None

    ctk.CTkLabel(frame, text="Tên đăng nhập:", text_color="black").pack(anchor="w", pady=2)
    entry_username_forgot = ctk.CTkEntry(frame, width=200)
    entry_username_forgot.pack(pady=2)

    ctk.CTkLabel(frame, text="Mã Nhân Viên (MaNV):", text_color="black").pack(anchor="w", pady=2)
    entry_manv_forgot = ctk.CTkEntry(frame, width=200)
    entry_manv_forgot.pack(pady=2)

    def request_otp():
        nonlocal temp_otp, temp_username, temp_email
        username = entry_username_forgot.get()
        manv_str = entry_manv_forgot.get()

        if not username or not manv_str:
            messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
            return

        try:
            manv = int(manv_str)
        except ValueError:
            messagebox.showerror("Lỗi", "Mã Nhân Viên phải là số nguyên!")
            return

        users = load_users()
        user = next((u for u in users if u.TDN == username), None)
        if not user:
            messagebox.showerror("Lỗi", "Tên đăng nhập không tồn tại!")
            return

        try:
            nhanvien_bus = NhanVienBUS()
            nhanvien = nhanvien_bus.find_nhan_vien_by_ma_nhan_vien(manv)
            print(f"Nhân viên: MNV={nhanvien.MNV}, HOTEN={nhanvien.HOTEN}, EMAIL={nhanvien.EMAIL}")
            if not nhanvien:
                messagebox.showerror("Lỗi", "Không tìm thấy thông tin nhân viên với MaNV này!")
                return
            temp_email = nhanvien.EMAIL
            if not temp_email:
                messagebox.showerror("Lỗi", "Nhân viên này chưa có email trong hệ thống!")
                return
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lấy thông tin nhân viên: {e}")
            return

        temp_otp = generate_otp()
        temp_username = username

        # Gửi OTP qua email hoặc hiển thị qua messagebox
        if USE_EMAIL:
            if send_otp_email(temp_email, temp_otp):
                messagebox.showinfo("Thành công", f"Mã OTP đã được gửi đến email: {temp_email}\nVui lòng kiểm tra email của bạn!")
            else:
                messagebox.showerror("Lỗi", "Không thể gửi mã OTP qua email. Vui lòng thử lại!")
        else:
            messagebox.showinfo("Thành công", f"Mã OTP: {temp_otp}\n(Vui lòng sử dụng mã này để đặt lại mật khẩu)")

        for widget in frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(frame, text="Nhập mã OTP:", text_color="black").pack(anchor="w", pady=2)
        entry_otp = ctk.CTkEntry(frame, width=200)
        entry_otp.pack(pady=2)

        ctk.CTkLabel(frame, text="Mật khẩu mới:", text_color="black").pack(anchor="w", pady=2)
        entry_new_password = ctk.CTkEntry(frame, show="*", width=200)
        entry_new_password.pack(pady=2)

        def verify_otp_and_reset():
            entered_otp = entry_otp.get()
            new_password = entry_new_password.get()

            if not entered_otp or not new_password:
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
                return

            if entered_otp != temp_otp:
                messagebox.showerror("Lỗi", "Mã OTP không đúng!")
                return

            users = load_users()
            user = next((u for u in users if u.TDN == temp_username), None)
            if not user:
                messagebox.showerror("Lỗi", "Tài khoản không tồn tại!")
                return

            try:
                result = TaiKhoanBUS().doi_mat_khau(user.MNV, hash_password(new_password))
                if result > 0:
                    messagebox.showinfo("Thành công", "Mật khẩu đã được đặt lại thành công!")
                    forgot_window.destroy()
                    fade_transition(root, lambda: root.deiconify(), new_geometry="500x250")
                else:
                    messagebox.showerror("Lỗi", "Không thể cập nhật mật khẩu: Không tìm thấy tài khoản phù hợp!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật mật khẩu: {e}")

        button_frame = ctk.CTkFrame(frame, fg_color="white")
        button_frame.pack(pady=10)

        btn_verify = ctk.CTkButton(button_frame, text="Xác nhận OTP", font=("Arial", 12, "bold"), fg_color="#008000", command=verify_otp_and_reset)
        btn_verify.grid(row=0, column=0, padx=5)
        btn_back = ctk.CTkButton(button_frame, text="Quay lại", font=("Arial", 12, "bold"), fg_color="#008000", command=lambda: back_to_login())
        btn_back.grid(row=0, column=1, padx=5)

    def back_to_login():
        forgot_window.destroy()
        fade_transition(root, lambda: root.deiconify(), new_geometry="500x250")

    button_frame = ctk.CTkFrame(frame, fg_color="white")
    button_frame.pack(pady=10)

    btn_request_otp = ctk.CTkButton(button_frame, text="Gửi mã OTP", font=("Arial", 12, "bold"), fg_color="#008000", command=request_otp)
    btn_request_otp.grid(row=0, column=0, padx=5)
    btn_back = ctk.CTkButton(button_frame, text="Quay lại", font=("Arial", 12, "bold"), fg_color="#008000", command=back_to_login)
    btn_back.grid(row=0, column=1, padx=5)

    forgot_window.grab_set()

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
    forgot_label.bind("<Button-1>", lambda e: open_forgot_password_window(root))

    btn_login = ctk.CTkButton(right_frame, text="Đăng nhập", font=("Arial", 14, "bold"), fg_color="#FFA500", command=lambda: login(root))
    btn_login.pack(pady=10, padx=50, fill="x")

    root.update()

if __name__ == "__main__":
    root = ctk.CTk()
    main(root)
    root.mainloop()