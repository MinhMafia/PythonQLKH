import customtkinter as ctk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from BUS.NhanVienBUS import NhanVienBUS
from DTO.NhanVienDTO import NhanVienDTO
import re
from datetime import datetime
from mysql.connector import Error

StaffBUS = NhanVienBUS()

# Danh sách chức vụ mẫu (lấy từ bảng CHUCVU)
CHUC_VU = {
    1: "Quản lý tổng",
    2: "Quản lý giao dịch",
    3: "Nhân viên giao dịch"
}

# Danh sách trạng thái
TRANG_THAI = {
    0: "Bị khóa",
    1: "Hoạt động",
    2: "Chưa xác thực"
}

def load_nhan_vien():
    staffs = StaffBUS.get_nhan_vien_all()
    # print("load_nhan_vien result:", [s.__dict__ for s in staffs])  # Log dữ liệu trả về
    return staffs

def check_sdt_exists(sdt, exclude_mnv=None):
    staffs = load_nhan_vien()
    for staff in staffs:
        if staff.SDT == sdt and (exclude_mnv is None or staff.MNV != exclude_mnv):
            return True
    return False

def check_email_exists(email, exclude_mnv=None):
    if not email:
        return False
    staffs = load_nhan_vien()
    for staff in staffs:
        if staff.EMAIL == email and (exclude_mnv is None or staff.MNV != exclude_mnv):
            return True
    return False

def Staff(frame_right):
    staffs = load_nhan_vien()

    def search_entry_event(event=None):
        keyword = search.get().strip().lower()
        update_table(filter_value=keyword)

    def search_button_event():
        keyword = search.get().strip().lower()
        update_table(filter_value=keyword)
        search.delete(0, "end")

    def reload_search():
        print("Reloading staff list from database")  # Log để kiểm tra
        staffs.clear()  # Xóa danh sách hiện tại
        staffs.extend(load_nhan_vien())  # Tải danh sách mới từ BUS
        search.delete(0, "end")  # Xóa ô tìm kiếm
        update_table()  # Cập nhật bảng
        if not staffs:
            messagebox.showinfo("Thông báo", "Không có nhân viên nào trong cơ sở dữ liệu.")
        # print("Reloaded staffs:", [s.__dict__ for s in staffs])  # Log danh sách sau khi tải

    def update_table(filter_value=None):
        table.delete(*table.get_children())
        if not staffs:
            staffs.extend(load_nhan_vien())  # Tải lại nếu danh sách rỗng
        for staff in staffs:
            if not filter_value or filter_value in str(staff).lower():
                status = TRANG_THAI.get(staff.TT, "Không xác định")
                table.insert("", "end", values=(
                    staff.MNV, staff.HOTEN, staff.SDT, staff.EMAIL,
                    staff.NGAYSINH, status))

    def open_staff_window(title, mode="detail", prefill_data=None):
        print(f"Opening window with title: {title}, mode: {mode}, prefill_data: {prefill_data.__dict__ if prefill_data else None}")  # Log khi mở cửa sổ
        win = ctk.CTkToplevel(frame_right)
        win.title(title)
        win.geometry("450x650")  # Tăng kích thước để đảm bảo đủ chỗ
        win.grab_set()

        ctk.CTkLabel(win, text=title, font=("Arial", 21), text_color="#00FA9A").pack(pady=10)

        form_frame = ctk.CTkFrame(win, fg_color="transparent")
        form_frame.pack(pady=8, fill="x", padx=10)

        fields = {}
        labels = ["Họ và Tên", "Giới tính", "Ngày sinh", "SĐT", "Email", "Chức vụ"]
        if mode == "edit":
            labels.append("Trạng thái")
        mandatory_fields = ["Họ và Tên", "Giới tính", "Ngày sinh", "SĐT", "Email", "Chức vụ"]

        for label_text in labels:
            label = ctk.CTkLabel(form_frame, text=f"{label_text}:", font=("Arial", 14))
            label.pack(pady=5)
            if label_text == "Giới tính":
                entry = ctk.CTkComboBox(form_frame, values=["Nam", "Nữ"], width=300)
            elif label_text == "Chức vụ":
                entry = ctk.CTkComboBox(form_frame, values=list(CHUC_VU.values()), width=300)
            elif label_text == "Trạng thái":
                entry = ctk.CTkComboBox(form_frame, values=list(TRANG_THAI.values()), width=300, state="normal")
            else:
                entry = ctk.CTkEntry(form_frame, width=300)
                
            entry.pack(pady=5)
            fields[label_text] = entry

        # Điền dữ liệu vào form
        if prefill_data:
            # print("Filling form with prefill_data:", prefill_data.__dict__)  # Log dữ liệu điền
            fields["Họ và Tên"].insert(0, prefill_data.HOTEN or "")
            fields["Giới tính"].set("Nam" if prefill_data.GIOITINH == 1 else "Nữ")
            fields["Ngày sinh"].insert(0, str(prefill_data.NGAYSINH) if prefill_data.NGAYSINH else "")
            fields["SĐT"].insert(0, prefill_data.SDT or "")
            fields["Email"].insert(0, prefill_data.EMAIL or "")
            fields["Chức vụ"].set(CHUC_VU.get(prefill_data.MCV, "Nhân viên giao dịch"))
            if mode == "edit" and "Trạng thái" in fields:
                fields["Trạng thái"].set(TRANG_THAI.get(prefill_data.TT, "Chưa xác thực"))
            # print("Form fields after filling:", {k: v.get() for k, v in fields.items()})  # Log trạng thái các trường

        # Vô hiệu hóa các entry và combobox sau khi điền dữ liệu
        if mode == "detail":
            for entry in fields.values():
                entry.configure(state="disabled")
        elif mode == "edit" and "Trạng thái" in fields:
            for label_text, entry in fields.items():
                if label_text != "Trạng thái":
                    entry.configure(state="disabled")

        def close_window():
            print("Closing window")  # Log khi đóng cửa sổ
            win.grab_release()
            win.destroy()

        def validate_inputs():
            for field in mandatory_fields:
                if not fields[field].get().strip():
                    messagebox.showerror("Lỗi", f"Vui lòng điền {field}.")
                    return False
            phone = fields["SĐT"].get().strip()
            if not re.match(r"^[0-9]{10}$", phone):
                messagebox.showerror("Lỗi", "Số điện thoại phải là 10 chữ số.")
                return False
            email = fields["Email"].get().strip()
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                messagebox.showerror("Lỗi", "Email không hợp lệ.")
                return False
            hoten = fields["Họ và Tên"].get().strip()
            if len(hoten) > 255:
                messagebox.showerror("Lỗi", "Họ và Tên không được vượt quá 255 ký tự.")
                return False
            if len(email) > 50:
                messagebox.showerror("Lỗi", "Email không được vượt quá 50 ký tự.")
                return False
            ngaysinh = fields["Ngày sinh"].get().strip()
            try:
                datetime.strptime(ngaysinh, "%Y-%m-%d")
                if datetime.strptime(ngaysinh, "%Y-%m-%d") > datetime.now():
                    messagebox.showerror("Lỗi", "Ngày sinh không được trong tương lai.")
                    return False
            except ValueError:
                messagebox.showerror("Lỗi", "Ngày sinh phải có định dạng YYYY-MM-DD.")
                return False
            if fields["Giới tính"].get() not in ["Nam", "Nữ"]:
                messagebox.showerror("Lỗi", "Vui lòng chọn giới tính hợp lệ.")
                return False
            chucvu = fields["Chức vụ"].get()
            if chucvu not in CHUC_VU.values():
                messagebox.showerror("Lỗi", "Vui lòng chọn chức vụ hợp lệ.")
                return False
            if mode == "edit" and fields["Trạng thái"].get() not in TRANG_THAI.values():
                messagebox.showerror("Lỗi", "Vui lòng chọn trạng thái hợp lệ.")
                return False
            # Kiểm tra SDT và Email tồn tại
            mnv = prefill_data.MNV if prefill_data else None
            if check_sdt_exists(phone, exclude_mnv=mnv):
                messagebox.showerror("Lỗi", f"Số điện thoại '{phone}' đã được sử dụng. Vui lòng nhập số khác.")
                return False
            if check_email_exists(email, exclude_mnv=mnv):
                messagebox.showerror("Lỗi", f"Email '{email}' đã được sử dụng. Vui lòng nhập email khác.")
                return False
            return True

        def save_staff():
            print("Saving staff, mode:", mode)  # Log khi lưu
            if not validate_inputs():
                return

            try:
                # Lấy MCV từ tên chức vụ
                mcv = next(key for key, value in CHUC_VU.items() if value == fields["Chức vụ"].get())
                # Lấy TT từ tên trạng thái (nếu có)
                tt = next(key for key, value in TRANG_THAI.items() if value == fields["Trạng thái"].get()) if mode == "edit" else (2 if mode == "add" else prefill_data.TT)
                
                nv_dto = NhanVienDTO(
                    MNV=prefill_data.MNV if prefill_data else 0,
                    HOTEN=fields["Họ và Tên"].get().strip(),
                    GIOITINH=1 if fields["Giới tính"].get() == "Nam" else 0,
                    NGAYSINH=fields["Ngày sinh"].get().strip(),
                    SDT=fields["SĐT"].get().strip(),
                    EMAIL=fields["Email"].get().strip(),
                    MCV=mcv,
                    TT=tt
                )
                print("Saving NhanVienDTO:", nv_dto.__dict__)  # Log dữ liệu DTO

                if mode == "add":
                    result = StaffBUS.add_nhan_vien(nv_dto)
                    if result:
                        messagebox.showinfo("Thành công", "Thêm nhân viên thành công!")
                        staffs.clear()
                        staffs.extend(load_nhan_vien())
                        update_table()
                        close_window()
                    else:
                        messagebox.showerror("Lỗi", "Không thể thêm nhân viên. Kiểm tra dữ liệu nhập.")
                elif mode == "edit":
                    result = StaffBUS.update_nhan_vien(nv_dto)
                    if result:
                        messagebox.showinfo("Thành công", "Cập nhật nhân viên thành công!")
                        staffs.clear()
                        staffs.extend(load_nhan_vien())
                        update_table()
                        close_window()
                    else:
                        messagebox.showerror("Lỗi", "Không thể cập nhật nhân viên. Có thể MNV không tồn tại hoặc dữ liệu không hợp lệ.")
            except Error as e:
                print(f"Database error: {e}")  # Log lỗi cơ sở dữ liệu
                if "Duplicate entry" in str(e):
                    if "SDT" in str(e):
                        messagebox.showerror("Lỗi", f"Số điện thoại '{fields['SĐT'].get().strip()}' đã được sử dụng. Vui lòng nhập số khác.")
                    elif "EMAIL" in str(e):
                        messagebox.showerror("Lỗi", f"Email '{fields['Email'].get().strip()}' đã được sử dụng. Vui lòng nhập email khác.")
                    else:
                        messagebox.showerror("Lỗi", "Dữ liệu nhập bị trùng. Kiểm tra SĐT hoặc Email.")
                elif "Data too long" in str(e):
                    if "HOTEN" in str(e):
                        messagebox.showerror("Lỗi", "Họ và Tên vượt quá độ dài cho phép (255 ký tự).")
                    elif "EMAIL" in str(e):
                        messagebox.showerror("Lỗi", "Email vượt quá độ dài cho phép (50 ký tự).")
                    else:
                        messagebox.showerror("Lỗi", f"Dữ liệu quá dài: {str(e)}")
                else:
                    messagebox.showerror("Lỗi", f"Lỗi cơ sở dữ liệu: {str(e)}")
            except Exception as e:
                print(f"General error: {e}")  # Log lỗi chung
                messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

        # Sử dụng grid để kiểm soát vị trí nút
        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=10, fill="x", padx=10)

        ctk.CTkButton(btn_frame, text="Hủy bỏ", fg_color="gray", command=close_window, width=120).grid(row=0, column=0, padx=10, sticky="w")
        if mode != "detail":
            ctk.CTkButton(btn_frame, text="Xác nhận", fg_color="green", command=save_staff, width=120).grid(row=0, column=1, padx=10, sticky="e")
        print("Buttons created, mode:", mode)  # Log khi tạo nút

    def open_addStaff_window():
        open_staff_window("Thêm nhân viên", mode="add")

    def open_selected_staff(mode="detail"):
        selected = table.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một nhân viên.")
            return

        data = table.item(selected[0], "values")
        print("Selected MNV:", data[0])  # Log MNV được chọn
        try:
            staff = StaffBUS.find_nhan_vien_by_ma_nhan_vien(int(data[0]))
            # print("Staff data:", staff.__dict__ if staff else None)  # Log dữ liệu nhân viên
            if staff:
                open_staff_window(f"{'Chi tiết' if mode == 'detail' else 'Sửa'} nhân viên", mode=mode, prefill_data=staff)
            else:
                messagebox.showerror("Lỗi", f"Không tìm thấy nhân viên với MNV={data[0]}. Vui lòng thử lại.")
        except Exception as e:
            print(f"Error fetching staff: {e}")  # Log lỗi lấy dữ liệu
            messagebox.showerror("Lỗi", f"Lỗi khi lấy dữ liệu nhân viên: {str(e)}")

    def delete_selected_staff():
        selected = table.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một nhân viên.")
            return

        data = table.item(selected[0], "values")
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn khóa nhân viên này?"):
            try:
                result = StaffBUS.delete_nhan_vien(int(data[0]))
                if result:
                    messagebox.showinfo("Thành công", "Khóa nhân viên thành công!")
                    staffs.clear()
                    staffs.extend(load_nhan_vien())
                    update_table()
                else:
                    messagebox.showerror("Lỗi", "Không thể khóa nhân viên. Có thể MNV không tồn tại.")
            except Exception as e:
                print(f"Error deleting staff: {e}")  # Log lỗi xóa
                messagebox.showerror("Lỗi", f"Lỗi khi khóa: {str(e)}")

    def on_select(event):
        btn_detail.configure(state="normal")
        btn_edit.configure(state="normal")
        btn_delete.configure(state="normal")

    frame_right.master.title("Quản lý nhân viên")

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

    ctk.CTkButton(frame_buttons, text="➕ Thêm", width=80, command=open_addStaff_window).pack(side="left", padx=10)
    btn_edit = ctk.CTkButton(frame_buttons, text="✏ Sửa", width=80, command=lambda: open_selected_staff(mode="edit"), state="disabled")
    btn_edit.pack(side="left", padx=10)
    btn_delete = ctk.CTkButton(frame_buttons, text="❌ Khóa", width=80, command=delete_selected_staff, state="disabled")
    btn_delete.pack(side="left", padx=10)
    btn_detail = ctk.CTkButton(frame_buttons, text="📄 Chi tiết", width=80, command=lambda: open_selected_staff(mode="detail"), state="disabled")
    btn_detail.pack(side="left", padx=10)

    columns = ("MNV", "Họ và Tên", "SĐT", "Email", "Ngày sinh", "Trạng thái")

    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 12))
    style.configure("Treeview.Heading", font=("Arial", 14, "bold"))

    table = ttk.Treeview(frame_body, columns=columns, show="headings", height=20)
    table.bind("<<TreeviewSelect>>", on_select)

    for col in columns:
        table.heading(col, text=col)
    table.column("MNV", width=50, anchor="center")
    table.column("Họ và Tên", width=200, anchor="w")
    table.column("SĐT", width=120, anchor="center")
    table.column("Email", width=200, anchor="center")
    table.column("Ngày sinh", width=120, anchor="center")
    table.column("Trạng thái", width=120, anchor="center")

    scroll = ttk.Scrollbar(frame_body, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scroll.set)

    table.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    scroll.pack(side="right", fill="y")

    update_table()