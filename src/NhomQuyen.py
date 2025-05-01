import customtkinter as ctk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from BUS.NhomQuyenBUS import NhomQuyenBUS
from BUS.ChiTietQuyenBUS import CTQuyenBUS
from BUS.DanhMucChucNangBUS import DanhMucChucNangBUS
from DTO.NhomQuyenDTO import NhomQuyenDTO
from DTO.ChiTietQuyenDTO import CTQuyenDTO
from mysql.connector import Error

# Khởi tạo BUS
nhom_quyen_bus = NhomQuyenBUS()
ct_quyen_bus = CTQuyenBUS()
danh_muc_chuc_nang_bus = DanhMucChucNangBUS()

# Danh sách hành động
HANH_DONG = ["create", "update", "delete", "view"]

def NhomQuyen(frame_right):
    nhom_quyen_list = nhom_quyen_bus.get_all_nhom_quyen()
    chuc_nang_list = danh_muc_chuc_nang_bus.get_all_chuc_nang()
    # Tạo dictionary CHUC_NANG từ danh sách chức năng
    CHUC_NANG = {chuc_nang.MCN: chuc_nang.TEN for chuc_nang in chuc_nang_list}
    print(f"Loaded CHUC_NANG: {CHUC_NANG}")

    def search_entry_event(event=None):
        keyword = search.get().strip().lower()
        update_table(filter_value=keyword)

    def search_button_event():
        keyword = search.get().strip().lower()
        update_table(filter_value=keyword)
        search.delete(0, "end")

    def reload_search():
        try:
            nhom_quyen_list.clear()
            nhom_quyen_list.extend(nhom_quyen_bus.get_all_nhom_quyen())
            search.delete(0, "end")
            update_table()
            messagebox.showinfo("Thông báo", "Tải lại danh sách nhóm quyền thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tải lại danh sách nhóm quyền: {str(e)}")

    def update_table(filter_value=None):
        table.delete(*table.get_children())
        for nq in nhom_quyen_list:
            if not filter_value or filter_value in str(nq.TEN).lower():
                table.insert("", "end", values=(nq.MNQ, nq.TEN, "Hoạt động" if nq.TT == 1 else "Không hoạt động"))

    def open_nhom_quyen_window(title, mode="detail", prefill_data=None):
        print(f"Opening window with title: {title}, mode: {mode}, prefill_data: {prefill_data.__dict__ if prefill_data else None}")
        win = ctk.CTkToplevel(frame_right)
        win.title(title)
        win.geometry("600x500")
        win.grab_set()

        ctk.CTkLabel(win, text=title, font=("Arial", 18, "bold")).pack(pady=10)

        # Form nhập tên nhóm quyền
        form_frame = ctk.CTkFrame(win, fg_color="transparent")
        form_frame.pack(pady=10, fill="x", padx=10)

        fields = {}
        labels = ["Tên nhóm quyền"]
        for label_text in labels:
            label = ctk.CTkLabel(form_frame, text=f"{label_text}:", font=("Arial", 14))
            label.pack(pady=5)
            entry = ctk.CTkEntry(form_frame, width=300)
            if mode == "detail":
                entry.configure(state="disabled")
            entry.pack(pady=5)
            fields[label_text] = entry

        # Điền dữ liệu vào trường Tên nhóm quyền
        if prefill_data:
            fields["Tên nhóm quyền"].insert(0, prefill_data.TEN)

        # Bảng checkbox cho quyền
        table_frame = ctk.CTkFrame(win, fg_color="transparent")
        table_frame.pack(pady=10, fill="both", expand=True, padx=10)

        # Tiêu đề bảng
        headers = ["Đơn mục chức năng"] + HANH_DONG
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(table_frame, text=header, font=("Arial", 14, "bold"))
            label.grid(row=0, column=col, padx=5, pady=5, sticky="w")

        # Danh sách quyền (checkbox)
        permissions = {}
        if prefill_data:
            ct_quyen_list = ct_quyen_bus.get_ct_quyen_by_mnq(prefill_data.MNQ)
            print(f"Permissions for MNQ {prefill_data.MNQ}: {[ctq.__dict__ for ctq in ct_quyen_list]}")
        else:
            ct_quyen_list = []

        for row, (mcn, ten_chuc_nang) in enumerate(CHUC_NANG.items(), 1):
            ctk.CTkLabel(table_frame, text=ten_chuc_nang, font=("Arial", 12)).grid(row=row, column=0, padx=5, pady=5, sticky="w")
            row_permissions = {}
            for col, hanh_dong in enumerate(HANH_DONG, 1):
                var = ctk.BooleanVar(value=False)
                if any(ctq.MCN == mcn and ctq.HANHDONG == hanh_dong for ctq in ct_quyen_list):
                    var.set(True)
                checkbox = ctk.CTkCheckBox(table_frame, text="", variable=var, onvalue=True, offvalue=False)
                if mode == "detail":
                    checkbox.configure(state="disabled")
                checkbox.grid(row=row, column=col, padx=5, pady=5)
                row_permissions[hanh_dong] = var
            permissions[mcn] = row_permissions

        def close_window():
            print("Closing window")
            win.grab_release()
            win.destroy()

        def validate_inputs():
            ten_nhom = fields["Tên nhóm quyền"].get().strip()
            if not ten_nhom:
                messagebox.showerror("Lỗi", "Vui lòng điền tên nhóm quyền.")
                return False
            if len(ten_nhom) > 50:
                messagebox.showerror("Lỗi", "Tên nhóm quyền không được vượt quá 50 ký tự.")
                return False
            return True

        def save_nhom_quyen():
            if not validate_inputs():
                return

            try:
                # Lưu thông tin nhóm quyền
                tt = 1  # Mặc định là Hoạt động
                nq_dto = NhomQuyenDTO(
                    MNQ=prefill_data.MNQ if prefill_data else 0,
                    TEN=fields["Tên nhóm quyền"].get().strip(),
                    TT=tt
                )
                print(f"Saving NhomQuyenDTO: {nq_dto.__dict__}")

                if mode == "add":
                    mnq = nhom_quyen_bus.add_nhom_quyen(nq_dto)
                    if mnq is None:
                        messagebox.showerror("Lỗi", "Không thể thêm nhóm quyền.")
                        return
                elif mode == "edit":
                    result = nhom_quyen_bus.update_nhom_quyen(nq_dto)
                    if result:
                        mnq = prefill_data.MNQ
                        # Xóa các quyền cũ trong CTQUYEN
                        ct_quyen_bus.delete_all_by_mnq(mnq)
                    else:
                        messagebox.showerror("Lỗi", "Không thể cập nhật nhóm quyền.")
                        return

                # Lưu các quyền vào CTQUYEN
                ct_quyen_added = []
                for mcn, hanh_dong_dict in permissions.items():
                    for hanh_dong, var in hanh_dong_dict.items():
                        if var.get():
                            ctq_dto = CTQuyenDTO(MNQ=mnq, MCN=mcn, HANHDONG=hanh_dong)
                            ct_quyen_added.append(ctq_dto.__dict__)
                            ct_quyen_bus.add_ct_quyen(ctq_dto)
                print(f"Added CTQuyenDTOs: {ct_quyen_added}")

                messagebox.showinfo("Thành công", f"{'Thêm' if mode == 'add' else 'Cập nhật'} nhóm quyền thành công!")
                nhom_quyen_list.clear()
                nhom_quyen_list.extend(nhom_quyen_bus.get_all_nhom_quyen())
                update_table()
                close_window()

            except Error as e:
                print(f"Database error: {e}")
                messagebox.showerror("Lỗi", f"Lỗi cơ sở dữ liệu: {str(e)}")
            except Exception as e:
                print(f"General error: {e}")
                messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

        # Nút Xác nhận và Hủy bỏ
        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=10, fill="x", padx=10)

        ctk.CTkButton(btn_frame, text="Hủy bỏ", fg_color="red", command=close_window, width=120).grid(row=0, column=0, padx=10, sticky="w")
        if mode != "detail":
            ctk.CTkButton(btn_frame, text="Xác nhận", fg_color="green", command=save_nhom_quyen, width=120).grid(row=0, column=1, padx=10, sticky="e")

    def open_add_nhom_quyen_window():
        open_nhom_quyen_window("Thêm nhóm quyền", mode="add")

    def open_selected_nhom_quyen(mode="detail"):
        selected = table.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một nhóm quyền.")
            return

        data = table.item(selected[0], "values")
        try:
            nq = nhom_quyen_bus.get_nhom_quyen_by_mnq(int(data[0]))
            if nq:
                open_nhom_quyen_window(f"{'Chi tiết' if mode == 'detail' else 'Sửa'} nhóm quyền", mode=mode, prefill_data=nq)
            else:
                messagebox.showerror("Lỗi", f"Không tìm thấy nhóm quyền với MNQ={data[0]}.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi lấy dữ liệu nhóm quyền: {str(e)}")

    def delete_selected_nhom_quyen():
        selected = table.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một nhóm quyền.")
            return

        data = table.item(selected[0], "values")
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa nhóm quyền này?"):
            try:
                result = nhom_quyen_bus.delete_nhom_quyen(int(data[0]))
                if result:
                    messagebox.showinfo("Thành công", "Xóa nhóm quyền thành công!")
                    nhom_quyen_list.clear()
                    nhom_quyen_list.extend(nhom_quyen_bus.get_all_nhom_quyen())
                    update_table()
                else:
                    messagebox.showerror("Lỗi", "Không thể xóa nhóm quyền.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa nhóm quyền: {str(e)}")

    def on_select(event):
        btn_detail.configure(state="normal")
        btn_edit.configure(state="normal")
        btn_delete.configure(state="normal")

    frame_right.master.title("Quản lý nhóm quyền")

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

    ctk.CTkButton(frame_buttons, text="➕ Thêm", width=80, command=open_add_nhom_quyen_window).pack(side="left", padx=10)
    btn_edit = ctk.CTkButton(frame_buttons, text="✏ Sửa", width=80, command=lambda: open_selected_nhom_quyen(mode="edit"), state="disabled")
    btn_edit.pack(side="left", padx=10)
    btn_delete = ctk.CTkButton(frame_buttons, text="❌ Xóa", width=80, command=delete_selected_nhom_quyen, state="disabled")
    btn_delete.pack(side="left", padx=10)
    btn_detail = ctk.CTkButton(frame_buttons, text="📄 Chi tiết", width=80, command=lambda: open_selected_nhom_quyen(mode="detail"), state="disabled")
    btn_detail.pack(side="left", padx=10)

    columns = ("MNQ", "Tên nhóm quyền", "Trạng thái")

    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 12))
    style.configure("Treeview.Heading", font=("Arial", 14, "bold"))

    table = ttk.Treeview(frame_body, columns=columns, show="headings", height=20)
    table.bind("<<TreeviewSelect>>", on_select)

    for col in columns:
        table.heading(col, text=col)
    table.column("MNQ", width=50, anchor="center")
    table.column("Tên nhóm quyền", width=200, anchor="w")
    table.column("Trạng thái", width=120, anchor="center")

    scroll = ttk.Scrollbar(frame_body, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scroll.set)

    table.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    scroll.pack(side="right", fill="y")

    update_table()