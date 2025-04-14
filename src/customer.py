import customtkinter as ctk
import tkinter.ttk as ttk
from BUS.KhachHangBUS import KhachHangBUS
import component as comp


def load_khach_hang():
    khachHangBUS = KhachHangBUS()
    return khachHangBUS.get_khach_hang_all()


def Customer(frame_right):
    customers = load_khach_hang()

    def search_entry_event(event=None):
        keyword = search.get().strip().lower()
        update_table(filter_value=keyword)

    def search_button_event():
        keyword = search.get().strip().lower()
        update_table(filter_value=keyword)
        search.delete(0, "end")

    def reload_search():
        search.delete(0, "end")
        update_table()

    def update_table(filter_value=None):
        table.delete(*table.get_children())
        for customer in customers:
            if not filter_value or filter_value in str(customer).lower():
                table.insert("", "end", values=(
                    customer.MKH, customer.HOTEN, customer.SDT, customer.NGAYTHAMGIA))

    def open_customer_window(title, disabled_fields=None, prefill_data=None):
        win = ctk.CTkToplevel(frame_right)
        win.title(title)
        comp.CanGiuaCuaSo(win, 400, 500)
        win.grab_set()

        ctk.CTkLabel(win, text=title, font=("Arial", 24), text_color="#00FA9A").pack(pady=10)

        form_frame = ctk.CTkFrame(win, fg_color="transparent")
        form_frame.pack(pady=10)

        fields = {}
        labels = ["Mã Căn cước công dân", "Họ và Tên", "SĐT", "Email", "Địa chỉ"]

        for label_text in labels:
            label = ctk.CTkLabel(form_frame, text=f"{label_text}:", font=("Arial", 14))
            label.pack(pady=5)
            entry = ctk.CTkEntry(form_frame, width=300)
            entry.pack(pady=5)
            fields[label_text] = entry

        if disabled_fields:
            for field in disabled_fields:
                fields[field].configure(state="disabled")

        if prefill_data:
            fields["Mã Căn cước công dân"].insert(0, prefill_data[0])
            fields["Họ và Tên"].insert(0, prefill_data[1])
            fields["SĐT"].insert(0, prefill_data[2])
            fields["Email"].insert(0, prefill_data[3])
            fields["Địa chỉ"].insert(0, "Địa chỉ mẫu")

        def close_window():
            win.grab_release()
            win.destroy()

        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="Hủy bỏ", fg_color="gray", command=close_window).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Xác nhận", fg_color="green", command=close_window).pack(side="right", padx=10)

    def open_selected_customer(mode="detail"):
        selected = table.selection()
        if not selected:
            return

        data = table.item(selected[0], "values")
        if mode == "detail":
            open_customer_window("Chi tiết khách hàng",
                                 disabled_fields=["Mã Căn cước công dân", "Họ và Tên", "SĐT", "Email", "Địa chỉ"],
                                 prefill_data=data)
        elif mode == "edit":
            open_customer_window("Sửa thông tin",
                                 disabled_fields=["Mã Căn cước công dân"],
                                 prefill_data=data)

    def on_select(event):
        btnDetail.configure(state="normal")

    frame_right.master.title("Quản lý khách hàng")

    frame_head = ctk.CTkFrame(frame_right, height=100, fg_color="#C8A280")
    frame_head.pack(fill="x")

    frame_body = ctk.CTkFrame(frame_right, fg_color="#A67B5B")
    frame_body.pack(fill="both", expand=True)

    frame_search = ctk.CTkFrame(frame_head, fg_color="transparent")
    frame_search.pack(side="left", padx=10, pady=15)

    search = ctk.CTkEntry(frame_search, placeholder_text="Nhập nội dung tìm kiếm", width=180)
    search.pack(side="left", padx=5)
    search.bind("<KeyRelease>", search_entry_event)

    ctk.CTkButton(frame_search, text="🔍 Tìm kiếm", width=85, command=search_button_event).pack(side="left", padx=5)
    ctk.CTkButton(frame_search, text="⟳", width=5, height=5, command=reload_search).pack(side="right", padx=5)

    frame_buttons = ctk.CTkFrame(frame_head, fg_color="transparent")
    frame_buttons.pack(side="right", padx=10, pady=10)

    ctk.CTkButton(frame_buttons, text="➕ Thêm", width=80, command=lambda: open_customer_window("Thêm khách hàng")).pack(side="left", padx=10)
    ctk.CTkButton(frame_buttons, text="✏ Sửa", width=80, command=lambda: open_selected_customer(mode="edit")).pack(side="left", padx=10)
    ctk.CTkButton(frame_buttons, text="❌ Xóa", width=80).pack(side="left", padx=10)
    btnDetail = ctk.CTkButton(frame_buttons, text="📄 Chi tiết", width=80, command=lambda: open_selected_customer(mode="detail"))
    btnDetail.pack(side="left", padx=10)

    columns = ("MKH", "Họ và Tên", "SĐT", "Ngày tham gia")

    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 14))
    style.configure("Treeview.Heading", font=("Arial", 16, "bold"))

    table = ttk.Treeview(frame_body, columns=columns, show="headings", height=20)
    table.bind("<<TreeviewSelect>>", on_select)

    for col in columns:
        table.heading(col, text=col)
    table.column("MKH", width=50, anchor="center")
    table.column("Họ và Tên", width=250, anchor="w")
    table.column("SĐT", width=150, anchor="center")
    table.column("Ngày tham gia", width=250, anchor="center")

    scroll = ttk.Scrollbar(frame_body, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scroll.set)

    table.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scroll.pack(side="right", fill="y")

    update_table()
