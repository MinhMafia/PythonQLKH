import customtkinter as ctk
import tkinter as ttk

def CustomerTest(frame_right):
    frame_right.master.title("KH test")

    frame_head_customer = ctk.CTkFrame(
        frame_right, width=750, height=100, fg_color="#C8A280")
    frame_head_customer.pack(fill="x")

    frame_body_customer = ctk.CTkFrame(
        frame_right, width=750, height=550, fg_color="#A67B5B")
    frame_body_customer.pack(fill="both", expand=True)

    # phần search
    frame_search = ctk.CTkFrame(
        frame_head_customer, fg_color="red")
    frame_search.pack(side="left", padx=10, pady=15)

    search = ctk.CTkEntry(frame_search,
                          placeholder_text="Nhập nội dung tìm kiếm", width=180)
    search.pack(side="left", padx=5)
    searchBtn = ctk.CTkButton(
        frame_search, text="Tìm kiếm", width=85)
    searchBtn.pack(side="left", padx=5)

    searchReload = ctk.CTkButton(frame_search,text="⟳",width=5, height=5)
    searchReload.pack(side="right",padx=5)

    # Frame chứa các nút
    frame_buttons = ctk.CTkFrame(
        frame_head_customer, fg_color="green")
    frame_buttons.pack(side="right", padx=10, pady=10)

    btnThem = ctk.CTkButton(frame_buttons,
                            text="Thêm", width=80, height=25)
    btnThem.pack(side="left", padx=10, pady=10)
    btnSua = ctk.CTkButton(frame_buttons,
                           text="Sửa", width=80, height=25)
    btnSua.pack(side="left", padx=10, pady=10)

    btnXoa = ctk.CTkButton(frame_buttons,
                           text="Xóa", width=80, height=25)
    btnXoa.pack(side="left", padx=10, pady=10)

    btnDetail = ctk.CTkButton(
        frame_buttons, text="Chi tiết", width=80, height=25)
    btnDetail.pack(side="left", padx=10, pady=10)

    columns = ("ID", "Họ và Tên", "SĐT", "Email")

    style = ttk.Style()
    # Kích cỡ chữ của nội dung bảng
    
    table = ttk.Treeview(frame_body_customer,
                         columns=columns, show="headings", height=20)

    # Định nghĩa tiêu đề cột
    table.heading("ID", text="ID")
    table.heading("Họ và Tên", text="Họ và Tên")
    table.heading("SĐT", text="SĐT")
    table.heading("Email", text="Email")

    # Căn chỉnh độ rộng cột
    table.column("ID", width=50, anchor="center")
    table.column("Họ và Tên", width=250, anchor="w")
    table.column("SĐT", width=150, anchor="center")
    table.column("Email", width=250, anchor="w")


    # Hiển thị bảng và thanh cuộn
    table.pack(side="left", fill="both", expand=True, padx=10, pady=10)

