import customtkinter as ctk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from BUS.ChucVuBUS import ChucVuBUS
from DTO.ChucVuDTO import ChucVuDTO
import re
from unidecode import unidecode


chucVuBUS = ChucVuBUS()

def load_chuc_vu():
    return chucVuBUS.get_chuc_vu_all()

def ChucVu(frame_right, quyenChucVu):

    listQuyenChucVu = quyenChucVu

    chuc_vus = load_chuc_vu()

    def search_entry_event(event=None):
        keyword = search.get().strip().lower()
        update_table(filter_value=keyword)

    def search_button_event():
        keyword = search.get().strip().lower()
        update_table(filter_value=keyword)
        search.delete(0, "end")

    def reload_search():
        chuc_vus.clear()  # Xóa danh sách hiện tại
        chuc_vus.extend(load_chuc_vu())  # Tải danh sách mới từ BUS
        search.delete(0, "end")  # Xóa ô tìm kiếm
        update_table()  # Cập nhật bảng
        if not chuc_vus:
            messagebox.showinfo("Thông báo", "Không có chức vụ nào trong cơ sở dữ liệu.")

    def update_table(filter_value=None):
        table.delete(*table.get_children())
        if not chuc_vus:
            chuc_vus.extend(load_chuc_vu())  # Tải lại nếu danh sách rỗng
        for chuc_vu in chuc_vus:
            if not filter_value or (
                unidecode(filter_value) in unidecode(chuc_vu.MCV.lower()) or
                unidecode(filter_value) in unidecode(chuc_vu.TEN.lower()) 
            ):
                status = ("Bị khóa" if chuc_vu.TT == 0 else 
                         "Hoạt động" if chuc_vu.TT == 1 else 
                         "Chưa xác thực")
                table.insert("", "end", values=(
                    chuc_vu.MCV, chuc_vu.TEN, f"{chuc_vu.MUCLUONG:,} VNĐ", status))

    def open_chucvu_window(title, mode="detail", prefill_data=None):
        win = ctk.CTkToplevel(frame_right)
        win.title(title)
        win.geometry("400x400")
        win.grab_set()

        ctk.CTkLabel(win, text=title, font=("Arial", 24), text_color="#00FA9A").pack(pady=10)

        form_frame = ctk.CTkFrame(win, fg_color="transparent")
        form_frame.pack(pady=10)

        fields = {}
        labels = ["Tên chức vụ", "Mức lương"]
        
        for label_text in labels:
            label = ctk.CTkLabel(form_frame, text=f"{label_text}:", font=("Arial", 14))
            label.pack(pady=5)
            entry = ctk.CTkEntry(form_frame, width=300)
            entry.pack(pady=5)
            fields[label_text] = entry

        # Thêm field trạng thái nếu là edit mode
        if mode == "edit":
            label = ctk.CTkLabel(form_frame, text="Trạng thái:", font=("Arial", 14))
            label.pack(pady=5)
            status_var = ctk.StringVar(value="Hoạt động")
            status_combobox = ctk.CTkComboBox(form_frame, width=300, 
                                              values=["Hoạt động", "Bị khóa", "Chưa xác thực"],
                                              variable=status_var)
            status_combobox.pack(pady=5)
            fields["Trạng thái"] = status_combobox

        # Điền dữ liệu vào form
        if prefill_data:
            fields["Tên chức vụ"].insert(0, prefill_data.TEN or "")
            fields["Mức lương"].insert(0, str(prefill_data.MUCLUONG or ""))
            
            if mode == "edit" and "Trạng thái" in fields:
                status_text = "Hoạt động"
                if prefill_data.TT == 0:
                    status_text = "Bị khóa"
                elif prefill_data.TT == 2:
                    status_text = "Chưa xác thực"
                status_var.set(status_text)

        # Vô hiệu hóa các entry sau khi điền dữ liệu
        if mode == "detail":    
            for entry in fields.values():
                entry.configure(state="disabled")

        def close_window():
            win.grab_release()
            win.destroy()

        def validate_inputs():
            # Kiểm tra các trường bắt buộc
            if not fields["Tên chức vụ"].get().strip():
                messagebox.showerror("Lỗi", "Vui lòng điền Tên chức vụ.")
                return False

            # Kiểm tra mức lương là số hợp lệ
            try:
                mucluong = int(fields["Mức lương"].get().strip().replace(',', ''))
                if mucluong < 0:
                    messagebox.showerror("Lỗi", "Mức lương không được âm.")
                    return False
            except ValueError:
                messagebox.showerror("Lỗi", "Mức lương phải là số nguyên.")
                return False

            ten = fields["Tên chức vụ"].get().strip()
            if len(ten) > 255:
                messagebox.showerror("Lỗi", "Tên chức vụ không được vượt quá 255 ký tự.")
                return False
            
            return True

        def save_chucvu():
            if not validate_inputs():
                return

            try:
                tt_value = 1  # Mặc định là hoạt động
                if mode == "edit" and "Trạng thái" in fields:
                    status_text = fields["Trạng thái"].get()
                    if status_text == "Bị khóa":
                        tt_value = 0
                    elif status_text == "Chưa xác thực":
                        tt_value = 2
                
                mucluong = int(fields["Mức lương"].get().strip().replace(',', ''))
                
                cv_dto = ChucVuDTO(
                    MCV=prefill_data.MCV if prefill_data else 0,
                    TEN=fields["Tên chức vụ"].get().strip(),
                    MUCLUONG=mucluong,
                    TT=tt_value
                )

                if mode == "add":
                    result = chucVuBUS.add_chuc_vu(cv_dto)
                    if result:
                        messagebox.showinfo("Thành công", "Thêm chức vụ thành công!")
                        chuc_vus.clear()
                        chuc_vus.extend(load_chuc_vu())
                        update_table()
                        close_window()
                    else:
                        messagebox.showerror("Lỗi", "Không thể thêm chức vụ. Kiểm tra dữ liệu nhập.")
                elif mode == "edit":
                    result = chucVuBUS.update_chuc_vu(cv_dto)
                    if result:
                        messagebox.showinfo("Thành công", "Cập nhật chức vụ thành công!")
                        chuc_vus.clear()
                        chuc_vus.extend(load_chuc_vu())
                        update_table()
                        close_window()
                    else:
                        messagebox.showerror("Lỗi", "Không thể cập nhật chức vụ. Có thể MCV không tồn tại hoặc dữ liệu không hợp lệ.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=15)

        if mode != "detail":
            ctk.CTkButton(btn_frame, text="Xác nhận", fg_color="green", command=save_chucvu).pack(side="right", padx=10)
        ctk.CTkButton(btn_frame, text="Hủy bỏ", fg_color="gray", command=close_window).pack(side="left", padx=10)

    def open_add_chucvu_window():
        open_chucvu_window("Thêm chức vụ", mode="add")

    def open_selected_chucvu(mode="detail"):
        selected = table.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một chức vụ.")
            return

        data = table.item(selected[0], "values")
        try:
            chuc_vu = chucVuBUS.find_chuc_vu_by_ma_chuc_vu(int(data[0]))
            if chuc_vu:
                open_chucvu_window(f"{'Chi tiết' if mode == 'detail' else 'Sửa'} chức vụ", mode=mode, prefill_data=chuc_vu)
            else:
                messagebox.showerror("Lỗi", f"Không tìm thấy chức vụ với MCV={data[0]}. Vui lòng thử lại.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lấy dữ liệu chức vụ: {str(e)}")

    def delete_selected_chucvu():
        selected = table.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một chức vụ.")
            return

        data = table.item(selected[0], "values")
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa chức vụ này?"):
            try:
                result = chucVuBUS.delete_chuc_vu(int(data[0]))
                if result:
                    messagebox.showinfo("Thành công", "Xóa chức vụ thành công!")
                    chuc_vus.clear()
                    chuc_vus.extend(load_chuc_vu())
                    update_table()
                else:
                    messagebox.showerror("Lỗi", "Không thể xóa chức vụ. Có thể MCV không tồn tại.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa: {str(e)}")

    def on_select(event):
        btn_detail.configure(state="normal")
        btn_edit.configure(state="normal")
        btn_delete.configure(state="normal")

    frame_right.master.title("Quản lý chức vụ")

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

    if any(q.HANHDONG == "create" for q in listQuyenChucVu):
        btn_add = ctk.CTkButton(frame_buttons, text="➕ Thêm", width=80, command=open_add_chucvu_window)
        btn_add.pack(side="left", padx=10)

    if any(q.HANHDONG == "update" for q in listQuyenChucVu):
        btn_edit = ctk.CTkButton(frame_buttons, text="✏ Sửa", width=80, command=lambda: open_selected_chucvu(mode="edit"), state="disabled")
        btn_edit.pack(side="left", padx=10)

    if any(q.HANHDONG == "delete" for q in listQuyenChucVu):
        btn_delete = ctk.CTkButton(frame_buttons, text="❌ Xóa", width=80, command=delete_selected_chucvu, state="disabled")
        btn_delete.pack(side="left", padx=10)

    if any(q.HANHDONG == "view" for q in listQuyenChucVu):
        btn_detail = ctk.CTkButton(frame_buttons, text="📄 Chi tiết", width=80, command=lambda: open_selected_chucvu(mode="detail"), state="disabled")
        btn_detail.pack(side="left", padx=10)

    columns = ("MCV", "Tên chức vụ", "Mức lương", "Trạng thái")

    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 11))
    style.configure("Treeview.Heading", font=("Arial", 13, "bold"))

    table = ttk.Treeview(frame_body, columns=columns, show="headings", height=20)
    table.bind("<<TreeviewSelect>>", on_select)

    for col in columns:
        table.heading(col, text=col)
    table.column("MCV", width=50, anchor="center")
    table.column("Tên chức vụ", width=200, anchor="w")
    table.column("Mức lương", width=150, anchor="center")
    table.column("Trạng thái", width=100, anchor="center")

    scroll = ttk.Scrollbar(frame_body, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scroll.set)

    table.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scroll.pack(side="right", fill="y")

    update_table()