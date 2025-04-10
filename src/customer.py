import customtkinter as ctk
import tkinter.ttk as ttk

from BUS.KhachHangBUS import KhachHangBUS
import component as comp

def load_khachHang():
    khachHangBUS = KhachHangBUS()  # Tạo đối tượng
    return khachHangBUS.get_khach_hang_all()  # Gọi phương thức qua đối tượng


def Customer(frame_right):

    customers = load_khachHang()


    # Phần def
    # def cho phần search khi viết
    def searchCustomerEntry(event=None):
        searchValue = search.get().strip().lower()

        for row in table.get_children():
            table.delete(row)

        for customer in data:
            if searchValue in str(customer).lower():
                table.insert("", "end", values=customer)

    # def cho phần search khi nhấn button
    def searchCustomerBtn():
        searchValue = search.get().strip().lower()

        for row in table.get_children():
            table.delete(row)

        for customer in data:
            if searchValue in str(customer).lower():
                table.insert("", "end", values=customer)

        search.delete(0, "end")

    def search_reload():
        search.delete(0, "end")

        for row in table.get_children():
            table.delete(row)

        data = database.fetch_customers()
        for row in data:
            table.insert("", "end", values=row)

    def window_add_customer():
        add_window = ctk.CTkToplevel(frame_right)
        # add_window.geometry("400x500")
        add_window.attributes("-topmost", True)
        comp.CanGiuaCuaSo(add_window, 400, 500)

        ctk.CTkLabel(add_window, text="Thêm khách hàng",
                     font=("Arial", 24), text_color="#00FA9A").pack(pady=8)

        ctk.CTkLabel(add_window, text="Mã Căn cước công dân:",
                     font=("Arial", 14)).pack(pady=5)
        entry_cccd = ctk.CTkEntry(add_window, width=300)
        entry_cccd.pack(pady=5)

        ctk.CTkLabel(add_window, text="Họ và Tên:",
                     font=("Arial", 14)).pack(pady=5)
        entry_name = ctk.CTkEntry(add_window, width=300)
        entry_name.pack(pady=5)

        ctk.CTkLabel(add_window, text="SĐT:", font=("Arial", 14)).pack(pady=5)
        entry_phone = ctk.CTkEntry(add_window, width=300)
        entry_phone.pack(pady=5)

        ctk.CTkLabel(add_window, text="Email:",
                     font=("Arial", 14)).pack(pady=5)
        entry_email = ctk.CTkEntry(add_window, width=300)
        entry_email.pack(pady=5)

        ctk.CTkLabel(add_window, text="Địa chỉ:",
                     font=("Arial", 14)).pack(pady=5)
        entry_address = ctk.CTkEntry(add_window, width=300)
        entry_address.pack(pady=5)

        frame_btn = ctk.CTkFrame(add_window, fg_color="transparent")
        frame_btn.pack(pady=15)

        btn_cancel = ctk.CTkButton(
            frame_btn, text="Hủy bỏ", fg_color="gray", command=add_window.destroy)
        btn_cancel.pack(side="left", padx=10)

        def confirm_action():
            print("Da them khach hang")
            add_window.destroy()

        btn_confirm = ctk.CTkButton(
            frame_btn, text="Xác nhận", fg_color="green", command=confirm_action)
        btn_confirm.pack(side="right", padx=10)

        add_window.grab_set()

    def window_edit_customer():
        selected_item = table.selection()
        if not selected_item:
            return
        add_window = ctk.CTkToplevel(frame_right)
        # add_window.geometry("400x500")
        add_window.attributes("-topmost", True)
        comp.CanGiuaCuaSo(add_window, 400, 500)

        ctk.CTkLabel(add_window, text="Sửa thông tin",
                     font=("Arial", 24), text_color="#00FA9A").pack(pady=8)

        ctk.CTkLabel(add_window, text="Mã Căn cước công dân:",
                     font=("Arial", 14)).pack(pady=5)
        entry_cccd = ctk.CTkEntry(add_window, width=300, state="disabled")
        entry_cccd.pack(pady=5)

        ctk.CTkLabel(add_window, text="Họ và Tên:",
                     font=("Arial", 14)).pack(pady=5)
        entry_name = ctk.CTkEntry(add_window, width=300)
        entry_name.pack(pady=5)

        ctk.CTkLabel(add_window, text="SĐT:", font=("Arial", 14)).pack(pady=5)
        entry_phone = ctk.CTkEntry(add_window, width=300)
        entry_phone.pack(pady=5)

        ctk.CTkLabel(add_window, text="Email:",
                     font=("Arial", 14)).pack(pady=5)
        entry_email = ctk.CTkEntry(add_window, width=300)
        entry_email.pack(pady=5)

        ctk.CTkLabel(add_window, text="Địa chỉ:",
                     font=("Arial", 14)).pack(pady=5)
        entry_address = ctk.CTkEntry(add_window, width=300)
        entry_address.pack(pady=5)

        frame_btn = ctk.CTkFrame(add_window, fg_color="transparent")
        frame_btn.pack(pady=15)

        btn_cancel = ctk.CTkButton(
            frame_btn, text="Hủy bỏ", fg_color="gray", command=add_window.destroy)
        btn_cancel.pack(side="left", padx=10)

        def confirm_action():
            print("Da them khach hang")
            add_window.destroy()

        btn_confirm = ctk.CTkButton(
            frame_btn, text="Xác nhận", fg_color="green", command=confirm_action)
        btn_confirm.pack(side="right", padx=10)

        add_window.grab_set()

    def window_detail_customer():
        selected_item = table.selection()
        if not selected_item:
            return
        add_window = ctk.CTkToplevel(frame_right)
        # add_window.geometry("400x500")
        add_window.attributes("-topmost", True)
        comp.CanGiuaCuaSo(add_window, 400, 500)

        ctk.CTkLabel(add_window, text="Chi tiết khách hàng",
                     font=("Arial", 24), text_color="#00FA9A").pack(pady=8)

        ctk.CTkLabel(add_window, text="Mã Căn cước công dân:",
                     font=("Arial", 14)).pack(pady=5)
        entry_cccd = ctk.CTkEntry(add_window, width=300, state="disabled")
        entry_cccd.pack(pady=5)

        ctk.CTkLabel(add_window, text="Họ và Tên:",
                     font=("Arial", 14)).pack(pady=5)
        entry_name = ctk.CTkEntry(add_window, width=300, state="disabled")
        entry_name.pack(pady=5)

        ctk.CTkLabel(add_window, text="SĐT:", font=("Arial", 14)).pack(pady=5)
        entry_phone = ctk.CTkEntry(add_window, width=300, state="disabled")
        entry_phone.pack(pady=5)

        ctk.CTkLabel(add_window, text="Email:",
                     font=("Arial", 14)).pack(pady=5)
        entry_email = ctk.CTkEntry(add_window, width=300, state="disabled")
        entry_email.pack(pady=5)

        ctk.CTkLabel(add_window, text="Địa chỉ:",
                     font=("Arial", 14)).pack(pady=5)
        entry_address = ctk.CTkEntry(add_window, width=300, state="disabled")
        entry_address.pack(pady=5)

        frame_btn = ctk.CTkFrame(add_window, fg_color="transparent")
        frame_btn.pack(pady=15)

        btn_cancel = ctk.CTkButton(
            frame_btn, text="Hủy bỏ", fg_color="gray", command=add_window.destroy)
        btn_cancel.pack(side="left", padx=10)

        def confirm_action():
            print("Da them khach hang")
            add_window.destroy()

        btn_confirm = ctk.CTkButton(
            frame_btn, text="Xác nhận", fg_color="green", command=confirm_action)
        btn_confirm.pack(side="right", padx=10)

        add_window.grab_set()

    def on_select(event):
        selected = table.selection()  # Lấy danh sách các dòng được chọn
        if selected:
            btnDetail.configure(state="normal")  # Bật nút nếu có dòng được chọn
        else:
            btnDetail.configure(state="disabled")  # Vô hiệu hóa nếu không có dòng nào được chọn

    #
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
    search.bind("<KeyRelease>", searchCustomerEntry)

    searchBtn = ctk.CTkButton(
        frame_search, text="🔍 Tìm kiếm", width=85, command=searchCustomerBtn)
    searchBtn.pack(side="left", padx=5)

    searchReload = ctk.CTkButton(frame_search,text="⟳",width=5, height=5,command= search_reload)
    searchReload.pack(side="right",padx=5)

    # Frame chứa các nút
    frame_buttons = ctk.CTkFrame(
        frame_head_customer, fg_color="transparent")
    frame_buttons.pack(side="right", padx=10, pady=10)

    btnThem = ctk.CTkButton(frame_buttons,
                            text="➕ Thêm", width=80, height=25, command=window_add_customer)
    btnThem.pack(side="left", padx=10, pady=10)
    btnSua = ctk.CTkButton(frame_buttons,
                           text="✏ Sửa", width=80, height=25, command=window_edit_customer)
    btnSua.pack(side="left", padx=10, pady=10)

    btnXoa = ctk.CTkButton(frame_buttons,
                           text="❌ Xóa", width=80, height=25)
    btnXoa.pack(side="left", padx=10, pady=10)

    btnDetail = ctk.CTkButton(
        frame_buttons, text="📄 Chi tiết", width=80, height=25, command=window_detail_customer)
    btnDetail.pack(side="left", padx=10, pady=10)

    # ---------------------- BẢNG DANH SÁCH KHÁCH HÀNG --------------
    columns = ("MKH", "Họ và Tên", "SĐT", "Email")

    style = ttk.Style()
    # Kích cỡ chữ của nội dung bảng
    style.configure("Treeview", font=("Arial", 14))
    style.configure("Treeview.Heading", font=(
        "Arial", 16, "bold"))  # Kích cỡ chữ của tiêu đề
    # Tạo Treeview (Bảng)
    table = ttk.Treeview(frame_body_customer,
                         columns=columns, show="headings", height=20)

    # Định nghĩa tiêu đề cột
    table.heading("MKH", text="MKH")
    table.heading("Họ và Tên", text="Họ và Tên")
    table.heading("SĐT", text="SĐT")
    table.heading("Email", text="Email")

    # Căn chỉnh độ rộng cột
    table.column("MKH", width=50, anchor="center")
    table.column("Họ và Tên", width=250, anchor="w")
    table.column("SĐT", width=150, anchor="center")
    table.column("Email", width=250, anchor="w")

    # Gán sự kiện chọn dòng trong bảng
    table.bind("<<TreeviewSelect>>", on_select)
    
    # Thêm dữ liệu mẫu
    for row in customers:
        table.insert("", "end", values=(row.MKH, row.HOTEN, row.SDT, row.EMAIL))

    # Thêm thanh cuộn (Scrollbar)
    scroll = ttk.Scrollbar(frame_body_customer,
                           orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scroll.set)

    # Hiển thị bảng và thanh cuộn
    table.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scroll.pack(side="right", fill="y")
