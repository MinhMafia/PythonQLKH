from PIL import Image
from pathlib import Path

import customtkinter as ctk
import tkinter.ttk as ttk

import component as comp
import KhachHang, NhanVien, TaiKhoan
import login
from YeuCauGiaoDich import TransactionRequestApp
# from verification import load_verification_interface
# from verification_new import load_verification_interface

class Home:
    def __init__(self):
        self.user = None

    ctk.set_appearance_mode("dark")  # Chế độ tối
    ctk.set_default_color_theme("blue")  # Chủ đề màu xanh

    # Đường dẫn thư mục hiện tại
    currentDir = Path(__file__).parent

    def fade_transition(self, root, callback, duration=300, new_geometry=None):
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
                    comp.CanGiuaCuaSo(root, target_width, target_height)
                callback()

        fade_in()

    def setup_home(self, root):
        root.title("Trang chủ")

        frame_left = ctk.CTkFrame(root, width=250, height=650, corner_radius=0)
        frame_left.pack(side="left", fill="y")

        frame_right = ctk.CTkFrame(root, width=750, height=650)
        frame_right.pack(side="right", fill="both", expand=True)

        def Home():
            # Tải ảnh từ file
            global home_image
            image_path = self.currentDir / "img" / "home_image.png"
            home_image = ctk.CTkImage(light_image=Image.open(image_path), size=(750, 650))

            # Tạo label chứa ảnh
            label = ctk.CTkLabel(frame_right, image=home_image, text="")
            label.pack(expand=True)

        def Verify():
            label = ctk.CTkLabel(frame_right, text="Xác Minh", font=("Arial", 50))
            label.pack(expand=True)

        # Hàm chuyển trang
        def show_frame(page):
            for widget in frame_right.winfo_children():
                widget.destroy()  # Xóa nội dung cũ

            try:
                match page:
                    case "Home":
                        Home()
                    case "Verify":
                        # Verify()
                        # load_verification_interface(frame_right)
                        from verification_new import SignatureVerificationApp
                        SignatureVerificationApp(frame_right)
                    case "Customer":
                        KhachHang.Customer(frame_right)
                    case "Staff":
                        NhanVien.Staff(frame_right)
                    case "Account":
                        TaiKhoan.Account(frame_right)
                    case "TransactionRequest":
                        # label = ctk.CTkLabel(frame_right, text="Yêu cầu giao dịch", font=("Arial", 50))
                        TransactionRequestApp(frame_right)
                    case _:
                        raise ValueError("Trang không tồn tại")
            except Exception as e:
                label = ctk.CTkLabel(frame_right, text=f"❌ Lỗi: {e}", font=("Arial", 20), text_color="red")
                label.pack(expand=True)

        # Hàm đăng xuất
        def logout():
            for widget in root.winfo_children():
                widget.destroy()
            ctk.set_appearance_mode("light")
            # Thêm hiệu ứng chuyển đổi với kích thước mới
            self.fade_transition(root, lambda: login.main(root), new_geometry="500x250")


        # Chia frame_left thanh 2
        frame_left_account = ctk.CTkFrame(frame_left, width=250, height=100)
        frame_left_account.pack(fill="x", pady=10)

        frame_left_menu = ctk.CTkFrame(frame_left, width=250, height=550)
        frame_left_menu.pack(fill="both", expand=True)

        # Mo ta user
        avatar_path = self.currentDir / "img" / "avatar.jpg"
        if avatar_path.exists():
            avatar_img = ctk.CTkImage(light_image=Image.open(avatar_path).resize((50, 50)))
        else:
            avatar_img = None  # Hoặc sử dụng ảnh mặc định

        # label chứa ảnh
        avatar_label = ctk.CTkLabel(frame_left_account, image=avatar_img, text="")
        avatar_label.pack(side="left", pady=10, padx=10)

        frame_text = ctk.CTkFrame(frame_left_account, fg_color="transparent")
        frame_text.pack(side="left", padx=5)

        username_label = ctk.CTkLabel(frame_text, text="Username", font=("Arial", 12, "bold"))
        username_label.pack(anchor="w")

        role_label = ctk.CTkLabel(frame_text, text="Role_user", font=("Arial", 12, "bold"))
        role_label.pack(anchor="w")

        # Thêm nút vào khung trái
        btnHome = ctk.CTkButton(frame_left_menu, text="🏠 Trang chủ", command=lambda: show_frame("Home"))
        btnHome.pack(pady=10, padx=20)

        btnVerify = ctk.CTkButton(frame_left_menu, text="Xác Minh", command=lambda: show_frame("Verify"))
        btnVerify.pack(pady=10, padx=20)

        btnCustomer = ctk.CTkButton(frame_left_menu, text="👤 Khách hàng", command=lambda: show_frame("Customer"))
        btnCustomer.pack(pady=10, padx=20)

        btnStaff = ctk.CTkButton(frame_left_menu, text="Nhân viên", command=lambda: show_frame("Staff"))
        btnStaff.pack(pady=10, padx=20)

        btnAccount = ctk.CTkButton(frame_left_menu, text="Tài khoản", command=lambda: show_frame("Account"))
        btnAccount.pack(pady=10, padx=20)

        btn_TransactionRequest = ctk.CTkButton(frame_left_menu, text="Yêu cầu giao dịch", command=lambda: show_frame("TransactionRequest"))
        btn_TransactionRequest.pack(pady=10, padx=20)



        """"Đăng xuất"""
        btnLogout = ctk.CTkButton(frame_left_menu, text="Đăng xuất", command=logout)
        btnLogout.pack(side="bottom", pady=10, padx=20)

        show_frame("Home")

        root.update()  # Cập nhật giao diện sau khi thay đổi các frame

    def homeRun(self, root, user):
        self.user = user
        root.title("Trang chủ")
        for widget in root.winfo_children():
            widget.destroy()
        self.setup_home(root)
