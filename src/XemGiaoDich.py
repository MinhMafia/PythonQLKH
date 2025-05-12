import customtkinter as ctk
from tkinter import ttk


def view_transactions(frame_right, giao_dich_bus):
    main_frame = ctk.CTkFrame(frame_right, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    title_label = ctk.CTkLabel(main_frame, text="Danh sách giao dịch", font=("Arial", 20, "bold"))
    title_label.pack(anchor="w", pady=10)

    search_frame = ctk.CTkFrame(main_frame)
    search_frame.pack(fill="x", pady=10)

    search_var = ctk.StringVar(value="Mã giao dịch")
    search_option = ctk.CTkOptionMenu(search_frame, values=["Mã giao dịch", "Mã khách hàng", "Mã nhân viên"], variable=search_var)
    search_option.pack(side="left", padx=5)

    search_text_var = ctk.StringVar()
    search_entry = ctk.CTkEntry(search_frame, placeholder_text="Nhập từ khóa tìm kiếm", textvariable=search_text_var)
    search_entry.pack(side="left", fill="x", expand=True, padx=5)

    tree_frame = ctk.CTkFrame(main_frame)
    tree_frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(tree_frame, columns=("MGD", "MKH", "MNV", "NgayGiaoDich", "Tien", "TienKH", "TrangThai"), show="headings")
    tree.heading("MGD", text="Mã GD")
    tree.heading("MKH", text="Mã KH")
    tree.heading("MNV", text="Mã NV")
    tree.heading("NgayGiaoDich", text="Ngày GD")
    tree.heading("Tien", text="Số tiền")
    tree.heading("TienKH", text="Số dư KH")
    tree.heading("TrangThai", text="Trạng thái")

    tree.column("MGD", width=50)
    tree.column("MKH", width=50)
    tree.column("MNV", width=50)
    tree.column("NgayGiaoDich", width=120)
    tree.column("Tien", width=100)
    tree.column("TienKH", width=100)
    tree.column("TrangThai", width=80)

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def update_table(transactions):
        for item in tree.get_children():
            tree.delete(item)
        for gd in transactions:
            status = {0: "Hủy", 1: "Thành công", 2: "Đang xử lý"}.get(gd.TT, "Không xác định")
            tree.insert("", "end", values=(gd.MGD, gd.MKH, gd.MNV, gd.NGAYGIAODICH, gd.TIEN, gd.TIENKH, status))

    def search_transactions(*args):
        search_text = search_text_var.get().strip()
        search_type = search_var.get()
        if not search_text:
            transactions = giao_dich_bus.get_giao_dich_all()
        else:
            transactions = giao_dich_bus.search(search_text, search_type)

        update_table(transactions)

    search_button = ctk.CTkButton(search_frame, text="Tìm kiếm", command=search_transactions)
    search_button.pack(side="left", padx=5)

    search_text_var.trace_add("write", search_transactions)

    transactions = giao_dich_bus.get_giao_dich_all()
    update_table(transactions)