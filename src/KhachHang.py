import customtkinter as ctk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from BUS.KhachHangBUS import KhachHangBUS
from DTO.KhachHangDTO import KhachHangDTO  # Sửa import
import re
from datetime import datetime
from mysql.connector import Error
import component as comp
from unidecode import unidecode

khachHangBUS = KhachHangBUS()

def load_khach_hang():
    customers = khachHangBUS.get_khach_hang_all()
    # print("load_khach_hang result:", [c.__dict__ for c in customers])  # Log dữ liệu trả về
    return customers

def check_sdt_exists(sdt, exclude_mkh=None):
    customers = load_khach_hang()
    for customer in customers:
        if customer.SDT == sdt and (exclude_mkh is None or customer.MKH != exclude_mkh):
            return True
    return False

def check_email_exists(email, exclude_mkh=None):
    if not email:
        return False
    customers = load_khach_hang()
    for customer in customers:
        if customer.EMAIL == email and (exclude_mkh is None or customer.MKH != exclude_mkh):
            return True
    return False

def Customer(frame_right, quyenKhachHang):

    listQuyenKhachHang = quyenKhachHang

    customers = load_khach_hang()

    def search_entry_event(event=None):
        keyword = search.get().strip().lower()
        update_table(filter_value=keyword)

    def search_button_event():
        keyword = search.get().strip().lower()
        update_table(filter_value=keyword)
        search.delete(0, "end")

    def reload_search():
        customers.clear()  # Xóa danh sách hiện tại
        customers.extend(load_khach_hang())  # Tải danh sách mới từ BUS
        search.delete(0, "end")  # Xóa ô tìm kiếm
        update_table()  # Cập nhật bảng
        if not customers:
            messagebox.showinfo("Thông báo", "Không có khách hàng nào trong cơ sở dữ liệu.")
        # print("Reloaded customers:", [c.__dict__ for c in customers])  # Log danh sách sau khi tải

    def update_table(filter_value=None):
        table.delete(*table.get_children())
        if not customers:
            customers.extend(load_khach_hang())  # Tải lại nếu danh sách rỗng
        for customer in customers:
            if not filter_value or (
                unidecode(filter_value) in unidecode(customer.HOTEN.lower()) or 
                unidecode(filter_value) in unidecode(customer.SDT.lower()) or 
                unidecode(filter_value) in unidecode(customer.CCCD.lower() if customer.CCCD else "")
            ):
                status = ("Bị khóa" if customer.TT == 0 else 
                         "Hoạt động" if customer.TT == 1 else 
                         "Chưa xác thực")
                table.insert("", "end", values=(
                    customer.MKH, customer.HOTEN, customer.SDT, customer.CCCD,
                    customer.NGAYTHAMGIA, status))

    def open_customer_window(title, mode="detail", prefill_data=None):
        win = ctk.CTkToplevel(frame_right)
        win.title(title)
        win.geometry("400x600")
        # comp.CanGiuaCuaSo(win, 400, 600)
        win.grab_set()

        ctk.CTkLabel(win, text=title, font=("Arial", 24), text_color="#00FA9A").pack(pady=10)

        form_frame = ctk.CTkFrame(win, fg_color="transparent")
        form_frame.pack(pady=10)

        fields = {}
        labels = []
        if(mode == "add"):
            labels = ["Mã Căn cước công dân", "Họ và Tên", "SĐT", "Email", "Địa chỉ"]
        elif(mode == "detail"):
            labels = ["Mã Căn cước công dân", "Họ và Tên", "SĐT", "Email", "Địa chỉ","Ngày tham gia","Số tiền"]
            win.geometry("400x700")
            # comp.CanGiuaCuaSo(win, 400, 700)
        elif(mode == "edit"):
            labels = ["Mã Căn cước công dân", "Họ và Tên", "SĐT", "Email", "Địa chỉ"]
            
        mandatory_fields = ["Họ và Tên", "SĐT"]  # Loại CCCD khỏi mandatory khi sửa

        for label_text in labels:
            label = ctk.CTkLabel(form_frame, text=f"{label_text}:", font=("Arial", 14))
            label.pack(pady=5)
            entry = ctk.CTkEntry(form_frame, width=300)
            entry.pack(pady=5)
            fields[label_text] = entry
            
            # if mode == "detail":
            #     entry.configure(state="readonly")
            # elif mode == "edit" and label_text == "Mã Căn cước công dân":
            #     entry.configure(state="readonly")

        # Điền dữ liệu vào form
        if prefill_data:
            # print("Prefill data:", prefill_data.__dict__)  # Log dữ liệu prefill_data
            fields["Mã Căn cước công dân"].insert(0, prefill_data.CCCD or "")
            fields["Họ và Tên"].insert(0, prefill_data.HOTEN or "")
            fields["SĐT"].insert(0, prefill_data.SDT or "")
            fields["Email"].insert(0, prefill_data.EMAIL or "")
            fields["Địa chỉ"].insert(0, prefill_data.DIACHI or "")
            if (mode != "edit"):
                fields["Ngày tham gia"].insert(0, prefill_data.NGAYTHAMGIA or "")
                fields["Số tiền"].insert(0, prefill_data.TIEN or 0)

        # Vô hiệu hóa các entry sau khi điền dữ liệu
        if mode == "detail":    
            for entry in fields.values():
                entry.configure(state="disabled")
        elif mode == "edit" and "Mã Căn cước công dân" in fields:
            fields["Mã Căn cước công dân"].configure(state="disabled")

        def close_window():
            win.grab_release()
            win.destroy()

        def validate_inputs():
            # Kiểm tra các trường bắt buộc (trừ CCCD khi sửa)
            check_fields = mandatory_fields
            if mode == "add":
                check_fields = check_fields + ["Mã Căn cước công dân"]
            for field in check_fields:
                if not fields[field].get().strip():
                    messagebox.showerror("Lỗi", f"Vui lòng điền {field}.")
                    return False
            phone = fields["SĐT"].get().strip()
            if not re.match(r"^[0-9]{10}$", phone):
                messagebox.showerror("Lỗi", "Số điện thoại phải là 10 chữ số.")
                return False
            email = fields["Email"].get().strip()
            if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                messagebox.showerror("Lỗi", "Email không hợp lệ.")
                return False
            if mode == "add":  # Chỉ kiểm tra CCCD khi thêm
                cccd = fields["Mã Căn cước công dân"].get().strip()
                if not re.match(r"^[0-9]{11}$", cccd):
                    messagebox.showerror("Lỗi", "CCCD phải là 11 chữ số.")
                    return False
            hoten = fields["Họ và Tên"].get().strip()
            if len(hoten) > 255:
                messagebox.showerror("Lỗi", "Họ và Tên không được vượt quá 255 ký tự.")
                return False
            diachi = fields["Địa chỉ"].get().strip()
            if diachi and len(diachi) > 255:
                messagebox.showerror("Lỗi", "Địa chỉ không được vượt quá 255 ký tự.")
                return False
            if email and len(email) > 50:
                messagebox.showerror("Lỗi", "Email không được vượt quá 50 ký tự.")
                return False
            # Kiểm tra SDT và Email tồn tại
            mkh = prefill_data.MKH if prefill_data else None
            if check_sdt_exists(phone, exclude_mkh=mkh):
                messagebox.showerror("Lỗi", f"Số điện thoại '{phone}' đã được sử dụng. Vui lòng nhập số khác.")
                return False
            if check_email_exists(email, exclude_mkh=mkh):
                messagebox.showerror("Lỗi", f"Email '{email}' đã được sử dụng. Vui lòng nhập email khác.")
                return False
            return True

        def save_customer():
            if not validate_inputs():
                return

            try:
                kh_dto = KhachHangDTO(
                    MKH=prefill_data.MKH if prefill_data else 0,
                    HOTEN=fields["Họ và Tên"].get().strip(),
                    NGAYTHAMGIA=(datetime.now().strftime("%Y-%m-%d") if mode == "add" 
                                else prefill_data.NGAYTHAMGIA),
                    DIACHI=fields["Địa chỉ"].get().strip() or None,
                    SDT=fields["SĐT"].get().strip(),
                    EMAIL=fields["Email"].get().strip() or None,
                    CCCD=(fields["Mã Căn cước công dân"].get().strip() if mode == "add" 
                          else prefill_data.CCCD),
                    TIEN=0 if mode == "add" else (prefill_data.TIEN if prefill_data else 0),
                    TT=2 if mode == "add" else (prefill_data.TT if prefill_data else 2)
                )

                if mode == "add":
                    result = khachHangBUS.add_khach_hang(kh_dto)
                    if result:
                        messagebox.showinfo("Thành công", "Thêm khách hàng thành công!")
                        customers.clear()
                        customers.extend(load_khach_hang())
                        update_table()
                        close_window()
                    else:
                        messagebox.showerror("Lỗi", "Không thể thêm khách hàng. Kiểm tra dữ liệu nhập.")
                elif mode == "edit":
                    result = khachHangBUS.update_khach_hang(kh_dto)
                    if result:
                        messagebox.showinfo("Thành công", "Cập nhật khách hàng thành công!")
                        customers.clear()
                        customers.extend(load_khach_hang())
                        update_table()
                        close_window()
                    else:
                        messagebox.showerror("Lỗi", "Không thể cập nhật khách hàng. Có thể MKH không tồn tại hoặc dữ liệu không hợp lệ.")
            except Error as e:
                if "Duplicate entry" in str(e):
                    if "SDT" in str(e):
                        messagebox.showerror("Lỗi", f"Số điện thoại '{fields['SĐT'].get().strip()}' đã được sử dụng. Vui lòng nhập số khác.")
                    elif "EMAIL" in str(e):
                        messagebox.showerror("Lỗi", f"Email '{fields['Email'].get().strip()}' đã được sử dụng. Vui lòng nhập email khác.")
                    else:
                        messagebox.showerror("Lỗi", "Dữ liệu nhập bị trùng. Kiểm tra CCCD, SĐT, hoặc Email.")
                elif "Data too long" in str(e):
                    if "CCCD" in str(e):
                        messagebox.showerror("Lỗi", "CCCD vượt quá độ dài cho phép (11 chữ số).")
                    elif "HOTEN" in str(e):
                        messagebox.showerror("Lỗi", "Họ và Tên vượt quá độ dài cho phép (255 ký tự).")
                    elif "DIACHI" in str(e):
                        messagebox.showerror("Lỗi", "Địa chỉ vượt quá độ dài cho phép (255 ký tự).")
                    elif "EMAIL" in str(e):
                        messagebox.showerror("Lỗi", "Email vượt quá độ dài cho phép (50 ký tự).")
                    else:
                        messagebox.showerror("Lỗi", f"Dữ liệu quá dài: {str(e)}")
                else:
                    messagebox.showerror("Lỗi", f"Lỗi cơ sở dữ liệu: {str(e)}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=15)

        if mode != "detail":
            ctk.CTkButton(btn_frame, text="Xác nhận", fg_color="green", command=save_customer).pack(side="right", padx=10)
        ctk.CTkButton(btn_frame, text="Hủy bỏ", fg_color="gray", command=close_window).pack(side="left", padx=10)

    def open_addCustomer_window():
        open_customer_window("Thêm khách hàng", mode="add")

    def open_selected_customer(mode="detail"):
        selected = table.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một khách hàng.")
            return

        data = table.item(selected[0], "values")
        print("Selected MKH:", data[0])  # Log MKH được chọn
        try:
            customer = khachHangBUS.find_khach_hang_by_ma_khach_hang(int(data[0]))
            # print("Customer data:", customer.__dict__ if customer else None)  # Log dữ liệu khách hàng
            if customer:
                open_customer_window(f"{'Chi tiết' if mode == 'detail' else 'Sửa'} khách hàng", mode=mode, prefill_data=customer)
            else:
                messagebox.showerror("Lỗi", f"Không tìm thấy khách hàng với MKH={data[0]}. Vui lòng thử lại.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lấy dữ liệu khách hàng: {str(e)}")

    def delete_selected_customer():
        selected = table.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một khách hàng.")
            return

        data = table.item(selected[0], "values")
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa khách hàng này?"):
            try:
                result = khachHangBUS.delete_khach_hang(int(data[0]))
                if result:
                    messagebox.showinfo("Thành công", "Xóa khách hàng thành công!")
                    customers.clear()
                    customers.extend(load_khach_hang())
                    update_table()
                else:
                    messagebox.showerror("Lỗi", "Không thể xóa khách hàng. Có thể MKH không tồn tại.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa: {str(e)}")

    def on_select(event):
        btn_detail.configure(state="normal")
        btn_edit.configure(state="normal")
        btn_delete.configure(state="normal")

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

    if any(q.HANHDONG == "create" for q in listQuyenKhachHang):
        btn_add = ctk.CTkButton(frame_buttons, text="➕ Thêm", width=80, command=open_addCustomer_window)
        btn_add.pack(side="left", padx=10)

    if any(q.HANHDONG == "update" for q in listQuyenKhachHang):
        btn_edit = ctk.CTkButton(frame_buttons, text="✏ Sửa", width=80, command=lambda: open_selected_customer(mode="edit"), state="disabled")
        btn_edit.pack(side="left", padx=10)

    if any(q.HANHDONG == "delete" for q in listQuyenKhachHang):
        btn_delete = ctk.CTkButton(frame_buttons, text="❌ Xóa", width=80, command=delete_selected_customer, state="disabled")
        btn_delete.pack(side="left", padx=10)

    if any(q.HANHDONG == "view" for q in listQuyenKhachHang):
        btn_detail = ctk.CTkButton(frame_buttons, text="📄 Chi tiết", width=80, command=lambda: open_selected_customer(mode="detail"), state="disabled")
        btn_detail.pack(side="left", padx=10)

    columns = ("MKH", "Họ và Tên", "SĐT", "CCCD", "Ngày tham gia", "Trạng thái")

    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 11))
    style.configure("Treeview.Heading", font=("Arial", 13, "bold"))

    table = ttk.Treeview(frame_body, columns=columns, show="headings", height=20)
    table.bind("<<TreeviewSelect>>", on_select)

    for col in columns:
        table.heading(col, text=col)
    table.column("MKH", width=50, anchor="center")
    table.column("Họ và Tên", width=200, anchor="w")
    table.column("SĐT", width=120, anchor="center")
    table.column("CCCD", width=120, anchor="center")
    table.column("Ngày tham gia", width=150, anchor="center")
    table.column("Trạng thái", width=120, anchor="center")

    scroll = ttk.Scrollbar(frame_body, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scroll.set)

    table.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scroll.pack(side="right", fill="y")

    update_table()