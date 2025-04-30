import customtkinter as ctk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from BUS.NhomQuyenBUS import NhomQuyenBUS
from DTO.NhomQuyenDTO import NhomQuyenDTO
from mysql.connector import Error

# Khởi tạo BUS
nhom_quyen_bus = NhomQuyenBUS()

def NhomQuyen(frame_right):
    nhom_quyen_list = nhom_quyen_bus.get_all_nhom_quyen()

    def search_entry_event(event=None):
        keyword = search.get().strip().lower()
        update_table(filter_value=keyword)

    def search_button_event():
        keyword = search.get().strip().lower()
        update_table(filter_value=keyword)
        search.delete(0, "end")

    def reload_search():
        try:
            # Tải lại danh sách nhóm quyền từ cơ sở dữ liệu
            nhom_quyen_list.clear()
            nhom_quyen_list.extend(nhom_quyen_bus.get_all_nhom_quyen())
            
            # Xóa nội dung ô tìm kiếm
            search.delete(0, "end")
            
            # Cập nhật lại bảng
            update_table()
            
            messagebox.showinfo("Thông báo", "Tải lại danh sách nhóm quyền thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tải lại danh sách nhóm quyền: {str(e)}")

    def update_table(filter_value=None):
        # Xóa tất cả các hàng trong bảng
        table.delete(*table.get_children())
        
        # Thêm dữ liệu mới vào bảng
        for nq in nhom_quyen_list:
            if not filter_value or filter_value in str(nq.TEN).lower():
                table.insert("", "end", values=(nq.MNQ, nq.TEN, "Hoạt động" if nq.TT == 1 else "Không hoạt động"))

    def open_nhom_quyen_window(title, mode="detail", prefill_data=None):
        win = ctk.CTkToplevel(frame_right)
        win.title(title)
        win.geometry("400x300")
        win.grab_set()

        ctk.CTkLabel(win, text=title, font=("Arial", 18, "bold")).pack(pady=10)

        form_frame = ctk.CTkFrame(win, fg_color="transparent")
        form_frame.pack(pady=10, fill="x", padx=10)

        fields = {}
        labels = ["Tên nhóm quyền", "Trạng thái"]
        for label_text in labels:
            label = ctk.CTkLabel(form_frame, text=f"{label_text}:", font=("Arial", 14))
            label.pack(pady=5)
            if label_text == "Trạng thái":
                entry = ctk.CTkComboBox(form_frame, values=["Hoạt động", "Không hoạt động"], width=300, state="normal" if mode != "detail" else "disabled")
            else:
                entry = ctk.CTkEntry(form_frame, width=300)
                if mode == "detail":
                    entry.configure(state="disabled")
            entry.pack(pady=5)
            fields[label_text] = entry

        # Điền dữ liệu vào form
        if prefill_data:
            fields["Tên nhóm quyền"].insert(0, prefill_data.TEN)
            fields["Trạng thái"].set("Hoạt động" if prefill_data.TT == 1 else "Không hoạt động")

        def close_window():
            win.grab_release()
            win.destroy()

        def validate_inputs():
            if not fields["Tên nhóm quyền"].get().strip():
                messagebox.showerror("Lỗi", "Vui lòng điền tên nhóm quyền.")
                return False
            return True

        def save_nhom_quyen():
            if not validate_inputs():
                return

            try:
                tt = 1 if fields["Trạng thái"].get() == "Hoạt động" else 0
                nq_dto = NhomQuyenDTO(
                    MNQ=prefill_data.MNQ if prefill_data else 0,
                    TEN=fields["Tên nhóm quyền"].get().strip(),
                    TT=tt
                )

                if mode == "add":
                    result = nhom_quyen_bus.add_nhom_quyen(nq_dto)
                    if result:
                        messagebox.showinfo("Thành công", "Thêm nhóm quyền thành công!")
                        nhom_quyen_list.clear()
                        nhom_quyen_list.extend(nhom_quyen_bus.get_all_nhom_quyen())
                        update_table()
                        close_window()
                    else:
                        messagebox.showerror("Lỗi", "Không thể thêm nhóm quyền.")
                elif mode == "edit":
                    result = nhom_quyen_bus.update_nhom_quyen(nq_dto)
                    if result:
                        messagebox.showinfo("Thành công", "Cập nhật nhóm quyền thành công!")
                        nhom_quyen_list.clear()
                        nhom_quyen_list.extend(nhom_quyen_bus.get_all_nhom_quyen())
                        update_table()
                        close_window()
                    else:
                        messagebox.showerror("Lỗi", "Không thể cập nhật nhóm quyền.")
            except Error as e:
                messagebox.showerror("Lỗi", f"Lỗi cơ sở dữ liệu: {str(e)}")

        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=10, fill="x", padx=10)

        ctk.CTkButton(btn_frame, text="Hủy bỏ", fg_color="gray", command=close_window, width=120).grid(row=0, column=0, padx=10, sticky="w")
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