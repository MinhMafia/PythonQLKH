import customtkinter as ctk
from pathlib import Path
from PIL import Image
from login import fade_transition
import login
from tkinter import ttk, messagebox
from datetime import datetime
from BUS.GiaoDichBUS import GiaoDichBUS
from DTO.GiaoDichDTO import GiaoDichDTO
from BUS.KhachHangBUS import KhachHangBUS

# Đường dẫn thư mục hiện tại
currentDir = Path(__file__).parent

def staffHomeRun(root):
    root.title("Giao diện Nhân viên")
    for widget in root.winfo_children():
        widget.destroy()  # Xóa giao diện cũ để chuyển sang giao diện nhân viên

    setup_staff_home(root)

def show_frame(page, frame_right, giao_dich_bus, khach_hang_bus):
    for widget in frame_right.winfo_children():
        widget.destroy()  # Xóa nội dung cũ

    try:
        match page:
            case "Dashboard":
                show_dashboard(frame_right, giao_dich_bus, khach_hang_bus)
            case "ViewTransactions":
                view_transactions(frame_right, giao_dich_bus)
            case "UpdateTransaction":
                update_transaction_status(frame_right, giao_dich_bus, khach_hang_bus)
            case "GenerateReport":
                generate_report(frame_right, giao_dich_bus)
            case _:
                raise ValueError("Trang không tồn tại")
    except Exception as e:
        label = ctk.CTkLabel(frame_right, text=f"❌ Lỗi: {e}", font=("Arial", 20), text_color="red")
        label.pack(expand=True)

def setup_staff_home(root):
    root.title("Giao diện Nhân viên")

    # Tạo frame trái (sidebar) với màu nền và bo góc
    frame_left = ctk.CTkFrame(root, width=250, height=650, corner_radius=10, fg_color="#2B2D42")
    frame_left.pack(side="left", fill="y", padx=10, pady=10)

    # Tạo frame phải (nội dung chính) với màu nền nhẹ
    frame_right = ctk.CTkFrame(root, width=750, height=650, fg_color="#EDF2F4", corner_radius=10)
    frame_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # Khởi tạo GiaoDichBUS và KhachHangBUS
    giao_dich_bus = GiaoDichBUS()
    khach_hang_bus = KhachHangBUS()

    # Hàm đăng xuất
    def logout():
        for widget in root.winfo_children():
            widget.destroy()
        ctk.set_appearance_mode("light")
        fade_transition(root, lambda: login.main(root), new_geometry="500x250")

    # Chia frame_left thành 2 phần
    frame_left_account = ctk.CTkFrame(frame_left, width=250, height=100, fg_color="transparent")
    frame_left_account.pack(fill="x", pady=20)

    frame_left_menu = ctk.CTkFrame(frame_left, width=250, height=550, fg_color="transparent")
    frame_left_menu.pack(fill="both", expand=True)

    # Mô tả user với avatar và thông tin
    avatar_path = currentDir / "img" / "avatar.jpg"
    if avatar_path.exists():
        avatar_img = ctk.CTkImage(light_image=Image.open(avatar_path).resize((60, 60)))
    else:
        avatar_img = None

    avatar_label = ctk.CTkLabel(frame_left_account, image=avatar_img, text="")
    avatar_label.pack(pady=10)

    frame_text = ctk.CTkFrame(frame_left_account, fg_color="transparent")
    frame_text.pack(pady=5)

    username_label = ctk.CTkLabel(frame_text, text="Nhân viên", font=("Arial", 14, "bold"), text_color="white")
    username_label.pack()

    role_label = ctk.CTkLabel(frame_text, text="Quản lý giao dịch", font=("Arial", 12), text_color="#D9E0E3")
    role_label.pack()

    # Thêm nút vào khung trái (sidebar) với hiệu ứng hover
    btnDashboard = ctk.CTkButton(frame_left_menu, text="🏠 Trang chủ", font=("Arial", 14), fg_color="#EF233C", hover_color="#D90429", corner_radius=8, command=lambda: show_frame("Dashboard", frame_right, giao_dich_bus, khach_hang_bus))
    btnDashboard.pack(pady=10, padx=20, fill="x")

    btnView = ctk.CTkButton(frame_left_menu, text="📋 Xem giao dịch", font=("Arial", 14), fg_color="#EF233C", hover_color="#D90429", corner_radius=8, command=lambda: show_frame("ViewTransactions", frame_right, giao_dich_bus, khach_hang_bus))
    btnView.pack(pady=10, padx=20, fill="x")

    btnUpdate = ctk.CTkButton(frame_left_menu, text="✏️ Cập nhật trạng thái", font=("Arial", 14), fg_color="#EF233C", hover_color="#D90429", corner_radius=8, command=lambda: show_frame("UpdateTransaction", frame_right, giao_dich_bus, khach_hang_bus))
    btnUpdate.pack(pady=10, padx=20, fill="x")

    btnReport = ctk.CTkButton(frame_left_menu, text="📊 Báo cáo", font=("Arial", 14), fg_color="#EF233C", hover_color="#D90429", corner_radius=8, command=lambda: show_frame("GenerateReport", frame_right, giao_dich_bus, khach_hang_bus))
    btnReport.pack(pady=10, padx=20, fill="x")

    btnLogout = ctk.CTkButton(frame_left_menu, text="Đăng xuất", font=("Arial", 14), fg_color="#8D99AE", hover_color="#6B7280", corner_radius=8, command=logout)
    btnLogout.pack(side="bottom", pady=20, padx=20, fill="x")

    # Hiển thị trang chủ mặc định
    show_frame("Dashboard", frame_right, giao_dich_bus, khach_hang_bus)
    root.update()

def show_dashboard(frame_right, giao_dich_bus, khach_hang_bus):
    main_frame = ctk.CTkFrame(frame_right, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Tiêu đề
    title_label = ctk.CTkLabel(main_frame, text="Chào mừng đến với Giao diện Nhân viên", font=("Arial", 28, "bold"), text_color="#2B2D42")
    title_label.pack(anchor="w", pady=(0, 10))

    # Thêm phần thông tin nhanh (dashboard summary)
    summary_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10)
    summary_frame.pack(fill="x", pady=10)

    # Lấy dữ liệu từ giao_dich_bus
    transactions = giao_dich_bus.get_giao_dich_all()
    today = datetime.now().date()
    today_transactions = [t for t in transactions if datetime.strptime(str(t.NGAYGIAODICH), "%Y-%m-%d %H:%M:%S").date() == today]
    total_amount_today = sum(t.TIEN for t in today_transactions if t.TT == 1)

    # Hiển thị thông tin nhanh
    ctk.CTkLabel(summary_frame, text=f"Giao dịch hôm nay: {len(today_transactions)}", font=("Arial", 16), text_color="#2B2D42").pack(anchor="w", padx=20, pady=5)
    ctk.CTkLabel(summary_frame, text=f"Tổng tiền (thành công): {total_amount_today} VND", font=("Arial", 16), text_color="#2B2D42").pack(anchor="w", padx=20, pady=5)

    # Gợi ý chọn chức năng
    welcome_label = ctk.CTkLabel(main_frame, text="Vui lòng chọn chức năng bên dưới hoặc từ menu bên trái:", font=("Arial", 16), text_color="#6B7280")
    welcome_label.pack(anchor="w", pady=(20, 10))

    # Thêm các nút chức năng trên trang chủ với icon và hiệu ứng hover
    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.pack(pady=20)

    # Nút Xem giao dịch
    btn_view_transactions = ctk.CTkButton(
        button_frame, 
        text="📋 Xem giao dịch", 
        font=("Arial", 16, "bold"), 
        fg_color="#EF233C", 
        hover_color="#D90429", 
        corner_radius=10, 
        width=220, 
        height=50, 
        command=lambda: show_frame("ViewTransactions", frame_right, giao_dich_bus, khach_hang_bus)
    )
    btn_view_transactions.grid(row=0, column=0, padx=15, pady=15)

    # Nút Cập nhật trạng thái
    btn_update_transaction = ctk.CTkButton(
        button_frame, 
        text="✏️ Cập nhật trạng thái", 
        font=("Arial", 16, "bold"), 
        fg_color="#EF233C", 
        hover_color="#D90429", 
        corner_radius=10, 
        width=220, 
        height=50, 
        command=lambda: show_frame("UpdateTransaction", frame_right, giao_dich_bus, khach_hang_bus)
    )
    btn_update_transaction.grid(row=0, column=1, padx=15, pady=15)

    # Nút Báo cáo
    btn_generate_report = ctk.CTkButton(
        button_frame, 
        text="📊 Báo cáo", 
        font=("Arial", 16, "bold"), 
        fg_color="#EF233C", 
        hover_color="#D90429", 
        corner_radius=10, 
        width=220, 
        height=50, 
        command=lambda: show_frame("GenerateReport", frame_right, giao_dich_bus, khach_hang_bus)
    )
    btn_generate_report.grid(row=0, column=2, padx=15, pady=15)

def view_transactions(frame_right, giao_dich_bus):
    main_frame = ctk.CTkFrame(frame_right, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    title_label = ctk.CTkLabel(main_frame, text="Danh sách giao dịch", font=("Arial", 20, "bold"))
    title_label.pack(anchor="w", pady=10)

    # Tạo frame tìm kiếm
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

def update_transaction_status(frame_right, giao_dich_bus, khach_hang_bus):
    main_frame = ctk.CTkFrame(frame_right, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    title_label = ctk.CTkLabel(main_frame, text="Cập nhật trạng thái giao dịch", font=("Arial", 20, "bold"))
    title_label.pack(anchor="w", pady=10)

    form_frame = ctk.CTkFrame(main_frame)
    form_frame.pack(fill="both", expand=True)

    ctk.CTkLabel(form_frame, text="Mã giao dịch (MGD):").pack(anchor="w", pady=5)
    entry_mgd = ctk.CTkEntry(form_frame)
    entry_mgd.pack(fill="x", pady=5)

    ctk.CTkLabel(form_frame, text="Trạng thái mới:").pack(anchor="w", pady=5)
    status_var = ctk.StringVar(value="1")
    ctk.CTkRadioButton(form_frame, text="Thành công", variable=status_var, value="1").pack(anchor="w", padx=20)
    ctk.CTkRadioButton(form_frame, text="Hủy", variable=status_var, value="0").pack(anchor="w", padx=20)
    ctk.CTkRadioButton(form_frame, text="Đang xử lý", variable=status_var, value="2").pack(anchor="w", padx=20)

    def submit():
        mgd = entry_mgd.get()
        new_status = status_var.get()

        if not mgd:
            messagebox.showerror("Lỗi", "Vui lòng nhập mã giao dịch!")
            return

        try:
            mgd = int(mgd)
            new_status = int(new_status)
        except ValueError:
            messagebox.showerror("Lỗi", "Mã giao dịch hoặc trạng thái không hợp lệ!")
            return

        gd = giao_dich_bus.find_giao_dich_by_ma_giao_dich(mgd)
        if not gd:
            messagebox.showerror("Lỗi", "Giao dịch không tồn tại!")
            return

        old_status = gd.TT
        mkh = gd.MKH
        tien = gd.TIEN

        customer = khach_hang_bus.get_khach_hang_by_id(mkh)
        if not customer:
            messagebox.showerror("Lỗi", "Khách hàng không tồn tại!")
            return

        current_balance = customer.TIEN

        if old_status in (1, 2) and new_status == 0:
            new_balance = current_balance - tien
            khach_hang_bus.update_tien(mkh, new_balance)
        elif old_status == 0 and new_status in (1, 2):
            new_balance = current_balance + tien
            if new_balance < 0:
                messagebox.showerror("Lỗi", "Số dư không đủ để hoàn tất giao dịch!")
                return
            khach_hang_bus.update_tien(mkh, new_balance)

        gd.TT = new_status
        try:
            giao_dich_bus.update_giao_dich(gd)
            messagebox.showinfo("Thành công", "Trạng thái giao dịch đã được cập nhật!")
            giao_dich_bus.listGiaoDich = GiaoDichBUS().get_giao_dich_all()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật trạng thái: {e}")

    ctk.CTkButton(form_frame, text="Cập nhật", command=submit).pack(pady=20)

def generate_report(frame_right, giao_dich_bus):
    main_frame = ctk.CTkFrame(frame_right, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    title_label = ctk.CTkLabel(main_frame, text="Báo cáo giao dịch", font=("Arial", 20, "bold"))
    title_label.pack(anchor="w", pady=5)

    filter_frame = ctk.CTkFrame(main_frame)
    filter_frame.pack(fill="x", pady=5)

    ctk.CTkLabel(filter_frame, text="Mã khách hàng (MKH, để trống để xem tất cả):").pack(anchor="w", pady=5)
    entry_mkh = ctk.CTkEntry(filter_frame, placeholder_text="Nhập MKH")
    entry_mkh.pack(fill="x", pady=5)

    ctk.CTkLabel(filter_frame, text="Từ ngày (YYYY-MM-DD):").pack(anchor="w", pady=5)
    entry_from_date = ctk.CTkEntry(filter_frame, placeholder_text="VD: 2024-01-01")
    entry_from_date.pack(fill="x", pady=5)

    ctk.CTkLabel(filter_frame, text="Đến ngày (YYYY-MM-DD):").pack(anchor="w", pady=5)
    entry_to_date = ctk.CTkEntry(filter_frame, placeholder_text="VD: 2024-12-31")
    entry_to_date.pack(fill="x", pady=5)

    report_frame = ctk.CTkFrame(main_frame)
    report_frame.pack(fill="both", expand=True)

    def update_report():
        for widget in report_frame.winfo_children():
            widget.destroy()

        mkh = entry_mkh.get().strip()
        from_date = entry_from_date.get().strip()
        to_date = entry_to_date.get().strip()

        transactions = giao_dich_bus.get_giao_dich_all()

        if mkh:
            try:
                mkh = int(mkh)
                transactions = [gd for gd in transactions if gd.MKH == mkh]
            except ValueError:
                messagebox.showerror("Lỗi", "Mã khách hàng không hợp lệ!")
                return

        try:
            if from_date:
                from_date = datetime.strptime(from_date, "%Y-%m-%d")
            if to_date:
                to_date = datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Lỗi", "Định dạng ngày không hợp lệ! Sử dụng YYYY-MM-DD.")
            return

        filtered_transactions = []
        for gd in transactions:
            try:
                gd_date = datetime.strptime(str(gd.NGAYGIAODICH), "%Y-%m-%d %H:%M:%S")
                if from_date and gd_date < from_date:
                    continue
                if to_date and gd_date > to_date:
                    continue
                filtered_transactions.append(gd)
            except ValueError:
                continue

        total_transactions = len(filtered_transactions)
        ctk.CTkLabel(report_frame, text=f"Tổng số giao dịch: {total_transactions}", font=("Arial", 14)).pack(anchor="w", pady=5)

        total_amount = sum(gd.TIEN for gd in filtered_transactions if gd.TT == 1)
        ctk.CTkLabel(report_frame, text=f"Tổng số tiền (giao dịch thành công): {total_amount} VND", font=("Arial", 14)).pack(anchor="w", pady=5)

        status_counts = {"Hủy": 0, "Thành công": 0, "Đang xử lý": 0}
        for gd in filtered_transactions:
            if gd.TT == 0:
                status_counts["Hủy"] += 1
            elif gd.TT == 1:
                status_counts["Thành công"] += 1
            elif gd.TT == 2:
                status_counts["Đang xử lý"] += 1

        for status, count in status_counts.items():
            ctk.CTkLabel(report_frame, text=f"Số giao dịch {status}: {count}", font=("Arial", 14)).pack(anchor="w", pady=5)

        tree_frame = ctk.CTkFrame(report_frame)
        tree_frame.pack(fill="both", expand=True, pady=5)

        # Tùy chỉnh style cho Treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 14), rowheight=30)  # Tăng font và chiều cao hàng
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))  # Tăng font cho tiêu đề cột

        tree = ttk.Treeview(tree_frame, columns=("MGD", "MKH", "MNV", "NgayGiaoDich", "Tien", "TienKH", "TrangThai"), show="headings")
        tree.heading("MGD", text="Mã GD")
        tree.heading("MKH", text="Mã KH")
        tree.heading("MNV", text="Mã NV")
        tree.heading("NgayGiaoDich", text="Ngày GD")
        tree.heading("Tien", text="Số tiền")
        tree.heading("TienKH", text="Số dư KH")
        tree.heading("TrangThai", text="Trạng thái")

        # Tăng chiều rộng cột
        tree.column("MGD", width=50)  # Tăng từ 50 lên 80
        tree.column("MKH", width=50)  # Tăng từ 50 lên 80
        tree.column("MNV", width=50)  # Tăng từ 50 lên 80
        tree.column("NgayGiaoDich", width=120)  # Tăng từ 120 lên 180
        tree.column("Tien", width=100)  # Tăng từ 100 lên 150
        tree.column("TienKH", width=100)  # Tăng từ 100 lên 150
        tree.column("TrangThai", width=80)  # Tăng từ 80 lên 120

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for gd in filtered_transactions:
            status = {0: "Hủy", 1: "Thành công", 2: "Đang xử lý"}.get(gd.TT, "Không xác định")
            tree.insert("", "end", values=(gd.MGD, gd.MKH, gd.MNV, gd.NGAYGIAODICH, gd.TIEN, gd.TIENKH, status))

    ctk.CTkButton(filter_frame, text="Tạo báo cáo", command=update_report).pack(pady=10)

    update_report()