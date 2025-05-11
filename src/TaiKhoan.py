import customtkinter as ctk
import tkinter.ttk as ttk
from tkinter import messagebox
from BUS.ChiTietQuyenBUS import CTQuyenBUS
from BUS.TaiKhoanBUS import TaiKhoanBUS
from BUS.NhanVienBUS import NhanVienBUS  # Nhập để kiểm tra MNV
import component as comp
import re
from login import hash_password  # Nhập hàm hash_password từ login.py

AccountBUS = TaiKhoanBUS()
NhanVienBUS = NhanVienBUS()
quanLyTaiKhoan = CTQuyenBUS()


def load_tai_khoan():
    return TaiKhoanBUS.get_tai_khoan_all()

def Account(frame_right):
    current_MNQ = user.MNQ
    listQuyenTaiKhoan = quanLyTaiKhoan.get_ct_quyen_by_mnq_and_mcn(current_MNQ, "taikhoan")

    accounts = load_tai_khoan()

    def update_table(filter_value=None):
        """Cập nhật bảng tài khoản."""
        table.delete(*table.get_children())
        for account in accounts:
            if not filter_value or filter_value in str(account).lower():
                table.insert("", "end", values=(
                    account.MNV, account.TDN, account.MNQ, account.TT))

    def open_account_window(title, disabled_fields=None, prefill_data=None):
        """Mở cửa sổ chi tiết hoặc chỉnh sửa tài khoản."""
        win = ctk.CTkToplevel(frame_right)
        win.title(title)
        comp.CanGiuaCuaSo(win, 400, 500)
        win.grab_set()

        ctk.CTkLabel(win, text=title, font=("Arial", 24), text_color="#00FA9A").pack(pady=10)

        form_frame = ctk.CTkFrame(win, fg_color="transparent")
        form_frame.pack(pady=10)

        fields = {}
        labels = ["Mã nhân viên", "Tên đăng nhập", "Mã nhóm quyền", "Trạng thái"]

        for label_text in labels:
            label = ctk.CTkLabel(form_frame, text=f"{label_text}:", font=("Arial", 14))
            label.pack(pady=5)
            entry = ctk.CTkEntry(form_frame, width=300)
            entry.pack(pady=5)
            fields[label_text] = entry


        if prefill_data:
            fields["Mã nhân viên"].insert(0, prefill_data[0])
            fields["Tên đăng nhập"].insert(0, prefill_data[1])
            fields["Mã nhóm quyền"].insert(0, prefill_data[2])
            fields["Trạng thái"].insert(0, prefill_data[3])

        if disabled_fields:
            for field in disabled_fields:
                fields[field].configure(state="disabled")
        def close_window():
            win.grab_release()
            win.destroy()

        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="Hủy bỏ", fg_color="gray", command=close_window).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Xác nhận", fg_color="green", command=close_window).pack(side="right", padx=10)

    def open_addaccount_window(title):
        """Mở cửa sổ thêm tài khoản."""
        win = ctk.CTkToplevel(frame_right)
        win.title(title)
        comp.CanGiuaCuaSo(win, 400, 500)
        win.grab_set()

        ctk.CTkLabel(win, text=title, font=("Arial", 24), text_color="#00FA9A").pack(pady=10)

        form_frame = ctk.CTkFrame(win, fg_color="transparent")
        form_frame.pack(pady=10)

        fields = {}
        labels = ["Mã nhân viên", "Tên đăng nhập", "Mật khẩu", "Mã nhóm quyền", "Trạng thái"]

        for label_text in labels:
            label = ctk.CTkLabel(form_frame, text=f"{label_text}:", font=("Arial", 14))
            label.pack(pady=5)
            entry = ctk.CTkEntry(form_frame, width=300, show="*" if label_text == "Mật khẩu" else "")
            entry.pack(pady=5)
            fields[label_text] = entry

        def close_window():
            win.grab_release()
            win.destroy()

        def add_account():
            """Thêm tài khoản mới."""
            mnv = fields["Mã nhân viên"].get().strip()
            tdn = fields["Tên đăng nhập"].get().strip()
            mk = fields["Mật khẩu"].get().strip()
            mnq = fields["Mã nhóm quyền"].get().strip()
            tt = fields["Trạng thái"].get().strip()

            # Kiểm tra dữ liệu đầu vào
            if not mnv.isdigit():
                comp.show_notify(False, "Mã nhân viên phải là số.")
                return

            if not tdn:
                comp.show_notify(False, "Tên đăng nhập không được để trống.")
                return

            if not mk:
                comp.show_notify(False, "Mật khẩu không được để trống.")
                return

            if not mnq.isdigit():
                comp.show_notify(False, "Mã nhóm quyền phải là số.")
                return

            if not tt.isdigit():
                comp.show_notify(False, "Trạng thái phải là số.")
                return

            if not AccountBUS.check_tdn(tdn):
                comp.show_notify(False, "Tên đăng nhập đã tồn tại.")
                return

            # Kiểm tra MNV tồn tại trong bảng NHANVIEN
            try:
                nhanvien = NhanVienBUS.find_nhan_vien_by_ma_nhan_vien(int(mnv))
                if not nhanvien:
                    comp.show_notify(False, "Mã nhân viên không tồn tại trong bảng NHANVIEN.")
                    return
            except Exception as e:
                comp.show_notify(False, f"Lỗi khi kiểm tra mã nhân viên: {e}")
                return

            # Băm mật khẩu
            hashed_password = hash_password(mk)
            print(f"Adding account - MNV: {mnv}, TDN: {tdn}, MK (hashed): {hashed_password}, MNQ: {mnq}, TT: {tt}")

            new_account = {
                "MNV": int(mnv),
                "TDN": tdn,
                "MK": hashed_password,
                "MNQ": int(mnq),
                "TT": int(tt),
            }

            try:
                AccountBUS.add_acc(new_account)
                comp.show_notify(True, "Thêm tài khoản thành công!")
                nonlocal accounts
                accounts = load_tai_khoan()
                update_table()
                close_window()
            except Exception as e:
                comp.show_notify(False, f"Không thể thêm tài khoản: {e}")
                print(f"Error adding account: {e}")

        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="Hủy bỏ", fg_color="gray", command=close_window).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Xác nhận", fg_color="green", command=add_account).pack(side="right", padx=10)

    def open_selected_account(mode="detail"):
        """Mở cửa sổ chi tiết hoặc chỉnh sửa tài khoản."""
        selected = table.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một tài khoản!")
            return
        
        data = table.item(selected[0], "values")

        if mode == "detail":
            open_account_window("Chi tiết tài khoản",
                                disabled_fields=["Mã nhân viên", "Tên đăng nhập", "Mã nhóm quyền", "Trạng thái"],
                                prefill_data=data)
        elif mode == "edit":
            open_account_window("Sửa thông tin tài khoản",
                                disabled_fields=["Mã nhân viên"],
                                prefill_data=data)
    
    def on_select(event):
        btn_detail.configure(state="normal")
        
        selected = table.selection()
        if not selected:
            return
        
        data = table.item(selected[0], "values")
        tenTaiKhoan = data[1].strip().lower()

        if tenTaiKhoan == "admin":
            btn_edit.configure(state="disabled")
            btn_delete.configure(state="disabled")
        else:
            btn_edit.configure(state="normal")
            btn_delete.configure(state="normal")

    frame_right.master.title("Quản lý tài khoản")

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

    if any(q.HANHDONG == "create" for q in listQuyenTaiKhoan):
        ctk.CTkButton(frame_buttons, text="➕ Thêm", width=80, command=lambda: open_addaccount_window("Thêm tài khoản")).pack(side="left", padx=10)
    
    if any(q.HANHDONG == "update" for q in listQuyenTaiKhoan):    
        btn_edit = ctk.CTkButton(frame_buttons, text="✏ Sửa", width=80, command=lambda: open_selected_account(mode="edit"), state="disabled")
        btn_edit.pack(side="left", padx=10)
    
    if any(q.HANHDONG == "delete" for q in listQuyenTaiKhoan):
        btn_delete = ctk.CTkButton(frame_buttons, text="❌ Xóa", width=80, state="disabled")
        btn_delete.pack(side="left", padx=10)

    if any(q.HANHDONG == "view" for q in listQuyenTaiKhoan):
        btn_detail = ctk.CTkButton(frame_buttons, text="📄 Chi tiết", width=80, command=lambda: open_selected_account(mode="detail"), state="disabled")
        btn_detail.pack(side="left", padx=10)

    columns = ("MNV", "Tên đăng nhập", "Mã nhóm quyền", "Trạng thái")

    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 14))
    style.configure("Treeview.Heading", font=("Arial", 16, "bold"))

    table = ttk.Treeview(frame_body, columns=columns, show="headings", height=20)
    table.bind("<<TreeviewSelect>>", on_select)


    for col in columns:
        table.heading(col, text=col)
    table.column("MNV", width=50, anchor="center")
    table.column("Tên đăng nhập", width=250, anchor="w")
    table.column("Mã nhóm quyền", width=150, anchor="center")
    table.column("Trạng thái", width=250, anchor="center")

    scroll = ttk.Scrollbar(frame_body, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scroll.set)

    table.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scroll.pack(side="right", fill="y")

    update_table()