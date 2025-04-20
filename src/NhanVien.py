import customtkinter as ctk
import tkinter.ttk as ttk
from tkinter import messagebox
from BUS.NhanVienBUS import NhanVienBUS
import component as comp
import re

StaffBUS = NhanVienBUS()

def load_nhan_vien():
    return StaffBUS.get_nhan_vien_all()

def Staff(frame_right):
    staffs = load_nhan_vien()

    def update_table(filter_value=None):
        """Cập nhật bảng nhân viên."""
        table.delete(*table.get_children())
        for staff in staffs:
            if not filter_value or filter_value in str(staff).lower():
                table.insert("", "end", values=(
                    staff.MNV, staff.HOTEN, staff.SDT, staff.EMAIL))

    def open_addstaff_window(title):
        """Mở cửa sổ thêm nhân viên."""
        win = ctk.CTkToplevel(frame_right)
        win.title(title)
        comp.CanGiuaCuaSo(win, 400, 500)
        win.grab_set()

        ctk.CTkLabel(win, text=title, font=("Arial", 24), text_color="#00FA9A").pack(pady=10)

        form_frame = ctk.CTkFrame(win, fg_color="transparent")
        form_frame.pack(pady=10)

        fields = {}
        labels = ["Họ và Tên", "SĐT", "Email", "Địa chỉ"]

        for label_text in labels:
            label = ctk.CTkLabel(form_frame, text=f"{label_text}:", font=("Arial", 14))
            label.pack(pady=5)
            entry = ctk.CTkEntry(form_frame, width=300)
            entry.pack(pady=5)
            fields[label_text] = entry

        def close_window():
            win.grab_release()
            win.destroy()

        def add_staff():
            """Thêm nhân viên mới."""
            name = fields["Họ và Tên"].get().strip()
            phone = fields["SĐT"].get().strip()
            email = fields["Email"].get().strip()
            address = fields["Địa chỉ"].get().strip()

            # Kiểm tra dữ liệu đầu vào
            if not re.match(r"^[0-9]{10}$", phone):
                comp.show_notify(False, "Số điện thoại không hợp lệ.")
                return

            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                comp.show_notify(False, "Email không hợp lệ.")
                return

            if not name or not phone or not email or not address:
                comp.show_notify(False, "Vui lòng điền đầy đủ thông tin.")
                return

            new_staff = {
                "HOTEN": name,
                "SDT": phone,
                "EMAIL": email,
                "DIACHI": address,
            }

            try:
                StaffBUS.add_nhan_vien(new_staff)
                comp.show_notify(True, "Thêm nhân viên thành công!")
                nonlocal staffs
                staffs = load_nhan_vien()
                update_table()
                close_window()
            except Exception as e:
                comp.show_notify(False, f"Không thể thêm nhân viên: {e}")

        # Nút Hủy và Xác nhận
        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="Hủy bỏ", fg_color="gray", command=close_window).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Xác nhận", fg_color="green", command=add_staff).pack(side="right", padx=10)

    def open_staff_window(title, disabled_fields=None, prefill_data=None):
        """Mở cửa sổ chi tiết hoặc chỉnh sửa nhân viên."""
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
            fields["Địa chỉ"].insert(0, prefill_data[4])

        def close_window():
            win.grab_release()
            win.destroy()

        # Nút Hủy và Xác nhận
        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="Hủy bỏ", fg_color="gray", command=close_window).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Xác nhận", fg_color="green", command=close_window).pack(side="right", padx=10)

    def open_selected_staff(mode="detail"):
        """Mở cửa sổ chi tiết hoặc chỉnh sửa nhân viên."""
        selected = table.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một nhân viên!")
            return

        data = table.item(selected[0], "values")
        if mode == "detail":
            open_staff_window("Chi tiết nhân viên",
                              disabled_fields=["Mã Căn cước công dân", "Họ và Tên", "SĐT", "Email", "Địa chỉ"],
                              prefill_data=data)
        elif mode == "edit":
            open_staff_window("Sửa thông tin nhân viên",
                              disabled_fields=["Mã Căn cước công dân"],
                              prefill_data=data)

    # Giao diện chính
    frame_right.master.title("Quản lý nhân viên")

    frame_head = ctk.CTkFrame(frame_right, height=100, fg_color="#C8A280")
    frame_head.pack(fill="x")

    frame_body = ctk.CTkFrame(frame_right, fg_color="#A67B5B")
    frame_body.pack(fill="both", expand=True)

    frame_search = ctk.CTkFrame(frame_head, fg_color="transparent")
    frame_search.pack(side="left", padx=10, pady=15)

    search = ctk.CTkEntry(frame_search, placeholder_text="Nhập nội dung tìm kiếm", width=180)
    search.pack(side="left", padx=5)
    search.bind("<KeyRelease>", lambda event: update_table(filter_value=search.get().strip().lower()))

    ctk.CTkButton(frame_search, text="🔍 Tìm kiếm", width=85, command=lambda: update_table(filter_value=search.get().strip().lower())).pack(side="left", padx=5)
    ctk.CTkButton(frame_search, text="⟳", width=5, height=5, command=lambda: update_table()).pack(side="right", padx=5)

    frame_buttons = ctk.CTkFrame(frame_head, fg_color="transparent")
    frame_buttons.pack(side="right", padx=10, pady=10)

    ctk.CTkButton(frame_buttons, text="➕ Thêm", width=80, command=lambda: open_addstaff_window("Thêm nhân viên")).pack(side="left", padx=10)
    ctk.CTkButton(frame_buttons, text="✏ Sửa", width=80, command=lambda: open_selected_staff(mode="edit")).pack(side="left", padx=10)
    ctk.CTkButton(frame_buttons, text="❌ Xóa", width=80).pack(side="left", padx=10)
    btnDetail = ctk.CTkButton(frame_buttons, text="📄 Chi tiết", width=80, command=lambda: open_selected_staff(mode="detail"))
    btnDetail.pack(side="left", padx=10)

    columns = ("MNV", "Họ và Tên", "SĐT", "Email")

    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 14))
    style.configure("Treeview.Heading", font=("Arial", 16, "bold"))

    table = ttk.Treeview(frame_body, columns=columns, show="headings", height=20)
    table.bind("<<TreeviewSelect>>", lambda event: btnDetail.configure(state="normal"))

    for col in columns:
        table.heading(col, text=col)
    table.column("MNV", width=50, anchor="center")
    table.column("Họ và Tên", width=250, anchor="w")
    table.column("SĐT", width=150, anchor="center")
    table.column("Email", width=250, anchor="center")

    scroll = ttk.Scrollbar(frame_body, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scroll.set)

    table.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scroll.pack(side="right", fill="y")

    update_table()