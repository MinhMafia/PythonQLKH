import customtkinter as ctk
import tkinter.ttk as ttk


def Customer(frame_right):
    frame_right.master.title("Quản lý khách hàng")

    # Chia frame_right thành head, body
    frame_head_customer = ctk.CTkFrame(
        frame_right, width=750, height=100, fg_color="#C8A280")
    frame_head_customer.pack(fill="x")

    frame_body_customer = ctk.CTkFrame(
        frame_right, width=750, height=550, fg_color="#A67B5B")
    frame_body_customer.pack(fill="both", expand=True)

    # phần search
    frame_search = ctk.CTkFrame(
        frame_head_customer, fg_color="transparent")
    frame_search.pack(side="left", padx=10, pady=15)

    search = ctk.CTkEntry(frame_search,
                          placeholder_text="Nhập nội dung tìm kiếm", width=180)
    search.pack(side="left", padx=5)

    searchBtn = ctk.CTkButton(frame_search, text="🔍 Tìm kiếm", width=85)
    searchBtn.pack(side="left", padx=5)

    # Frame chứa các nút
    frame_buttons = ctk.CTkFrame(
        frame_head_customer, fg_color="transparent")
    frame_buttons.pack(side="right", padx=10, pady=10)

    btnThem = ctk.CTkButton(frame_buttons,
                            text="➕ Thêm", width=80, height=25)
    btnThem.pack(side="left", padx=10, pady=10)
    btnSua = ctk.CTkButton(frame_buttons,
                           text="✏ Sửa", width=80, height=25)
    btnSua.pack(side="left", padx=10, pady=10)

    btnXoa = ctk.CTkButton(frame_buttons,
                           text="❌ Xóa", width=80, height=25)
    btnXoa.pack(side="left", padx=10, pady=10)

    btnDetail = ctk.CTkButton(
        frame_buttons, text="📄 Chi tiết", width=80, height=25)
    btnDetail.pack(side="left", padx=10, pady=10)

    # ---------------------- BẢNG DANH SÁCH KHÁCH HÀNG --------------
    columns = ("ID", "Họ và Tên", "SĐT", "Email")

    style = ttk.Style()
    # Kích cỡ chữ của nội dung bảng
    style.configure("Treeview", font=("Arial", 14))
    style.configure("Treeview.Heading", font=(
        "Arial", 16, "bold"))  # Kích cỡ chữ của tiêu đề
    # Tạo Treeview (Bảng)
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

 # Thêm dữ liệu mẫu
    data = [
        (1, "Nguyễn Văn A", "0123456789", "a@gmail.com"),
        (2, "Trần Thị B", "0987654321", "b@gmail.com"),
        (3, "Lê Văn C", "0345678901", "c@gmail.com"),
    ]
    for row in data:
        table.insert("", "end", values=row)

    # Thêm thanh cuộn (Scrollbar)
    scroll = ttk.Scrollbar(frame_body_customer,
                           orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scroll.set)

    # Hiển thị bảng và thanh cuộn
    table.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scroll.pack(side="right", fill="y")
