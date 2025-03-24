from PIL import Image
from pathlib import Path

import customtkinter as ctk
import tkinter.ttk as ttk

import component as comp
import customer

# Đường dẫn thư mục hiện tại
currentDir = Path(__file__).parent


def homeRun(root):
    root.title("Trang chủ")
    for widget in root.winfo_children():
        widget.destroy()  # Xóa giao diện cũ để chuyển sang home

    comp.CanGiuaCuaSo(root, 1000, 650)

    # Chia thành 2 Frame
    frame_left = ctk.CTkFrame(root, width=250, height=650, corner_radius=0)
    frame_left.pack(side="left", fill="y")

    global frame_right
    frame_right = ctk.CTkFrame(root, width=750, height=650)
    frame_right.pack(side="right", fill="both", expand=True)

    def Home():
        # Tải ảnh từ file
        global home_image
        image_path = currentDir / "images" / "home_image.png"
        home_image = ctk.CTkImage(light_image=Image.open(
            image_path), size=(750, 650))

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

        match page:
            case "Home":
                Home()
            case "Customer":
                customer.Customer(frame_right)
            case "Verify":
                Verify()
            case _:
                label = ctk.CTkLabel(
                    frame_right, text="❌ 404 Not Found", font=("Arial", 50))
                label.pack(expand=True)

    # Chia frame_left thanh 2

    frame_left_account = ctk.CTkFrame(frame_left, width=250, height=100)
    frame_left_account.pack(fill="x", pady=10)

    frame_left_menu = ctk.CTkFrame(frame_left, width=250, height=550)
    frame_left_menu.pack(fill="both", expand=True)

    # Mo ta user
    global avatar
    avatar_path = r"D:\Nam3_HK2\python\src\images\avatar.jpg"
    avatar_img = ctk.CTkImage(
        light_image=Image.open(avatar_path).resize((50, 50)))

    # label chứa ảnh
    avatar_label = ctk.CTkLabel(frame_left_account, image=avatar_img, text="")
    avatar_label.pack(side="left", pady=10, padx=10)

    frame_text = ctk.CTkFrame(frame_left_account, fg_color="transparent")
    frame_text.pack(side="left", padx=5)

    username_label = ctk.CTkLabel(
        frame_text, text="Username", font=("Arial", 12, "bold"))
    username_label.pack(anchor="w")

    role_label = ctk.CTkLabel(
        frame_text, text="Role_user", font=("Arial", 12, "bold"))
    role_label.pack(anchor="w")

    # Thêm nút vào khung trái
    btnHome = ctk.CTkButton(frame_left_menu, text="🏠 Trang chủ",
                            command=lambda: show_frame("Home"))
    btnHome.pack(pady=10, padx=20)

    btnCustomer = ctk.CTkButton(
        frame_left_menu, text="👤 Khách hàng", command=lambda: show_frame("Customer"))
    btnCustomer.pack(pady=10, padx=20)

    btnVerify = ctk.CTkButton(
        frame_left_menu, text="Xác Minh", command=lambda: show_frame("Verify"))
    btnVerify.pack(pady=10, padx=20)

    # Hiển thị trang chủ mặc định khi mở ứng dụng
    show_frame("Home")

    # def on_closing():
    #     root.destroy()  # Đóng cửa sổ Home
    #     root_login.deiconify()  # Hiển thị lại cửa sổ Login

    # root.protocol("WM_DELETE_WINDOW", on_closing)  # Gọi hàm khi nhấn nút X

    root.mainloop()


if __name__ == "__main__":
    root = ctk.CTk()
    homeRun(root)
