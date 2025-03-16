import customtkinter as ctk

root = ctk.CTk()
root.title("Trang chủ")


def CanGiuaCuaSo(window, width, height):
    window.resizable(width=False, height=False)
    screen_height = window.winfo_screenheight()
    screen_width = window.winfo_screenwidth()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")


CanGiuaCuaSo(root, 1000, 650)

# Chia thành 2 Frame
frame_left = ctk.CTkFrame(root, width=250, height=650, corner_radius=0)
frame_left.pack(side="left", fill="y")

frame_right = ctk.CTkFrame(root, width=750, height=650)
frame_right.pack(side="right", fill="both", expand=True)

# Hàm chuyển trang


def show_frame(page):
    for widget in frame_right.winfo_children():
        widget.destroy()  # Xóa nội dung cũ

    match page:
        case "Home":
            label = ctk.CTkLabel(
                frame_right, text="🏠 Trang chủ", font=("Arial", 50))
        case "Customer":
            label = ctk.CTkLabel(
                frame_right, text="👤 Quản lý khách hàng", font=("Arial", 50))
        case _:
            label = ctk.CTkLabel(
                frame_right, text="❌ 404 Not Found", font=("Arial", 50))

    label.pack(expand=True)  # Căn giữa nội dung


# Thêm nút vào khung trái
btnHome = ctk.CTkButton(frame_left, text="Trang chủ",
                        command=lambda: show_frame("Home"))
btnHome.pack(pady=10, padx=20)

btnCustomer = ctk.CTkButton(
    frame_left, text="Khách hàng", command=lambda: show_frame("Customer"))
btnCustomer.pack(pady=10, padx=20)

# Hiển thị trang chủ mặc định khi mở ứng dụng
show_frame("Home")

root.mainloop()
