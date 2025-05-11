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
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import csv
import logging

# Thiết lập logging
logging.basicConfig(level=logging.DEBUG, filename="app.log", filemode="a", format="%(asctime)s - %(levelname)s - %(message)s")

class Staff_home:
    def __init__(self):
        self.user = None
        self.currentDir = Path(__file__).parent

    def staffHomeRun(self, root, user):
        self.user = user
        root.title("Giao diện Nhân viên")
        for widget in root.winfo_children():
            widget.destroy()
        self.setup_staff_home(root)

    def show_frame(self, page, frame_right, giao_dich_bus, khach_hang_bus):
        for widget in frame_right.winfo_children():
            widget.destroy()
        try:
            match page:
                case "Dashboard":
                    self.show_dashboard(frame_right, giao_dich_bus, khach_hang_bus)
                case "ViewTransactions":
                    self.view_transactions(frame_right, giao_dich_bus)
                case "UpdateTransaction":
                    self.update_transaction_status(frame_right, giao_dich_bus, khach_hang_bus)
                case "GenerateReport":
                    self.generate_report(frame_right, giao_dich_bus)
                case _:
                    raise ValueError("Trang không tồn tại")
        except Exception as e:
            label = ctk.CTkLabel(frame_right, text=f"❌ Lỗi: {e}", font=("Arial", 20), text_color="red")
            label.pack(expand=True)

    def setup_staff_home(self, root):
        root.title("Giao diện Nhân viên")
        root.geometry("1000x700")

        frame_left = ctk.CTkFrame(root, width=250, height=650, corner_radius=10, fg_color="#2B2D42")
        frame_left.pack(side="left", fill="y", padx=10, pady=10)

        frame_right = ctk.CTkFrame(root, width=750, height=650, fg_color="#EDF2F4", corner_radius=10)
        frame_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        giao_dich_bus = GiaoDichBUS()
        khach_hang_bus = KhachHangBUS()

        def logout():
            for widget in root.winfo_children():
                widget.destroy()
            ctk.set_appearance_mode("light")
            fade_transition(root, lambda: login.main(root), new_geometry="500x250")

        frame_left_account = ctk.CTkFrame(frame_left, width=250, height=100, fg_color="transparent")
        frame_left_account.pack(fill="x", pady=20)

        frame_left_menu = ctk.CTkFrame(frame_left, width=250, height=550, fg_color="transparent")
        frame_left_menu.pack(fill="both", expand=True)

        avatar_path = self.currentDir / "img" / "avatar.jpg"
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

        btnDashboard = ctk.CTkButton(frame_left_menu, text="🏠 Trang chủ", font=("Arial", 14), fg_color="#EF233C", hover_color="#D90429", corner_radius=8, command=lambda: self.show_frame("Dashboard", frame_right, giao_dich_bus, khach_hang_bus))
        btnDashboard.pack(pady=10, padx=20, fill="x")

        btnView = ctk.CTkButton(frame_left_menu, text="📋 Xem giao dịch", font=("Arial", 14), fg_color="#EF233C", hover_color="#D90429", corner_radius=8, command=lambda: self.show_frame("ViewTransactions", frame_right, giao_dich_bus, khach_hang_bus))
        btnView.pack(pady=10, padx=20, fill="x")

        btnUpdate = ctk.CTkButton(frame_left_menu, text="✏️ Cập nhật trạng thái", font=("Arial", 14), fg_color="#EF233C", hover_color="#D90429", corner_radius=8, command=lambda: self.show_frame("UpdateTransaction", frame_right, giao_dich_bus, khach_hang_bus))
        btnUpdate.pack(pady=10, padx=20, fill="x")

        btnReport = ctk.CTkButton(frame_left_menu, text="📊 Báo cáo", font=("Arial", 14), fg_color="#EF233C", hover_color="#D90429", corner_radius=8, command=lambda: self.show_frame("GenerateReport", frame_right, giao_dich_bus, khach_hang_bus))
        btnReport.pack(pady=10, padx=20, fill="x")

        btnLogout = ctk.CTkButton(frame_left_menu, text="Đăng xuất", font=("Arial", 14), fg_color="#8D99AE", hover_color="#6B7280", corner_radius=8, command=logout)
        btnLogout.pack(side="bottom", pady=20, padx=20, fill="x")

        self.show_frame("Dashboard", frame_right, giao_dich_bus, khach_hang_bus)
        root.update()

    def show_dashboard(self, frame_right, giao_dich_bus, khach_hang_bus):
        main_frame = ctk.CTkFrame(frame_right, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(main_frame, text="Chào mừng đến với Giao diện Nhân viên", font=("Arial", 28, "bold"), text_color="#2B2D42")
        title_label.pack(anchor="w", pady=(0, 10))

        summary_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=10)
        summary_frame.pack(fill="x", pady=10)

        transactions = giao_dich_bus.get_giao_dich_all()
        today = datetime.now().date()
        today_transactions = [t for t in transactions if datetime.strptime(str(t.NGAYGIAODICH), "%Y-%m-%d %H:%M:%S").date() == today]
        total_amount_today = sum(t.TIEN for t in today_transactions if t.TT == 1)

        ctk.CTkLabel(summary_frame, text=f"Giao dịch hôm nay: {len(today_transactions)}", font=("Arial", 16), text_color="#2B2D42").pack(anchor="w", padx=20, pady=5)
        ctk.CTkLabel(summary_frame, text=f"Tổng tiền (thành công): {total_amount_today} VND", font=("Arial", 16), text_color="#2B2D42").pack(anchor="w", padx=20, pady=5)

        welcome_label = ctk.CTkLabel(main_frame, text="Vui lòng chọn chức năng bên dưới hoặc từ menu bên trái:", font=("Arial", 16), text_color="#6B7280")
        welcome_label.pack(anchor="w", pady=(20, 10))

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        btn_view_transactions = ctk.CTkButton(
            button_frame, 
            text="📋 Xem giao dịch", 
            font=("Arial", 16, "bold"), 
            fg_color="#EF233C", 
            hover_color="#D90429", 
            corner_radius=10, 
            width=220, 
            height=50, 
            command=lambda: self.show_frame("ViewTransactions", frame_right, giao_dich_bus, khach_hang_bus)
        )
        btn_view_transactions.grid(row=0, column=0, padx=15, pady=15)

        btn_update_transaction = ctk.CTkButton(
            button_frame, 
            text="✏️ Cập nhật trạng thái", 
            font=("Arial", 16, "bold"), 
            fg_color="#EF233C", 
            hover_color="#D90429", 
            corner_radius=10, 
            width=220, 
            height=50, 
            command=lambda: self.show_frame("UpdateTransaction", frame_right, giao_dich_bus, khach_hang_bus)
        )
        btn_update_transaction.grid(row=0, column=1, padx=15, pady=15)

        btn_generate_report = ctk.CTkButton(
            button_frame, 
            text="📊 Báo cáo", 
            font=("Arial", 16, "bold"), 
            fg_color="#EF233C", 
            hover_color="#D90429", 
            corner_radius=10, 
            width=220, 
            height=50, 
            command=lambda: self.show_frame("GenerateReport", frame_right, giao_dich_bus, khach_hang_bus)
        )
        btn_generate_report.grid(row=0, column=2, padx=15, pady=15)

    def view_transactions(self, frame_right, giao_dich_bus):
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

    def update_transaction_status(self, frame_right, giao_dich_bus, khach_hang_bus):
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

    def generate_report(self, frame_right, giao_dich_bus):
        main_frame = ctk.CTkFrame(frame_right, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title_label = ctk.CTkLabel(main_frame, text="📊 Báo cáo giao dịch", font=("Arial", 22, "bold"))
        title_label.pack(anchor="w", pady=10)

        form_container = ctk.CTkFrame(main_frame)
        form_container.pack(fill="x", pady=10)

        form_left = ctk.CTkFrame(form_container)
        form_left.pack(side="left", fill="x", expand=True, padx=(0, 10))

        form_right = ctk.CTkFrame(form_container)
        form_right.pack(side="left", fill="x", expand=True, padx=(10, 0))

        ctk.CTkLabel(form_left, text="🔎 Mã khách hàng (MKH):", font=("Arial", 14)).pack(anchor="w", pady=2)
        entry_mkh = ctk.CTkEntry(form_left, placeholder_text="Nhập MKH", takefocus=False)
        entry_mkh.pack(fill="x", pady=5)

        ctk.CTkLabel(form_left, text="📅 Từ ngày (YYYY-MM-DD):", font=("Arial", 14)).pack(anchor="w", pady=2)
        entry_from_date = ctk.CTkEntry(form_left, placeholder_text="VD: 2024-01-01", takefocus=False)
        entry_from_date.pack(fill="x", pady=5)

        ctk.CTkLabel(form_left, text="📅 Đến ngày (YYYY-MM-DD):", font=("Arial", 14)).pack(anchor="w", pady=2)
        entry_to_date = ctk.CTkEntry(form_left, placeholder_text="VD: 2024-12-31", takefocus=False)
        entry_to_date.pack(fill="x", pady=5)

        ctk.CTkLabel(form_right, text="📌 Trạng thái giao dịch:", font=("Arial", 14)).pack(anchor="w", pady=2)
        status_filter_var = ctk.StringVar(value="Tất cả")
        status_menu = ctk.CTkOptionMenu(form_right, values=["Tất cả", "Thành công", "Hủy", "Đang xử lý"], variable=status_filter_var)
        status_menu.pack(fill="x", pady=5)

        report_frame = ctk.CTkFrame(main_frame)
        report_frame.pack(fill="both", expand=True)

        chart_canvas = None

        def show_chart(status_data, chart_frame):
            nonlocal chart_canvas
            if all(value == 0 for value in status_data.values()):
                ctk.CTkLabel(report_frame, text="Không có dữ liệu để hiển thị biểu đồ", font=("Arial", 14), text_color="red").pack(pady=10)
                logging.warning("No data available for chart")
                return

            try:
                fig, ax = plt.subplots(figsize=(8, 5))
                labels = ["Thành công", "Hủy", "Đang xử lý"]
                values = [status_data[s] for s in labels]
                colors = ["green", "red", "orange"]

                ax.bar(labels, values, color=colors)
                ax.set_title("Số lượng giao dịch theo trạng thái", fontsize=14)
                ax.set_ylabel("Số giao dịch", fontsize=12)
                ax.tick_params(axis='both', which='major', labelsize=10)

                for i, v in enumerate(values):
                    ax.text(i, v + 0.1, str(v), ha='center', fontsize=10)

                plt.tight_layout()

                if chart_canvas:
                    chart_canvas.get_tk_widget().destroy()

                chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
                chart_canvas.draw()
                chart_canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)
                logging.debug("Chart displayed successfully")
                plt.close(fig)
            except Exception as e:
                logging.error(f"Error displaying chart: {str(e)}")
                ctk.CTkLabel(report_frame, text=f"Lỗi hiển thị biểu đồ: {str(e)}", font=("Arial", 14), text_color="red").pack(pady=10)

        def export_csv(transactions):
            path = "bao_cao_giao_dich.csv"
            with open(path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Mã GD", "Mã KH", "Mã NV", "Ngày GD", "Số tiền", "Số dư KH", "Trạng thái"])
                for gd in transactions:
                    status = {0: "Hủy", 1: "Thành công", 2: "Đang xử lý"}.get(gd.TT, "Không xác định")
                    writer.writerow([gd.MGD, gd.MKH, gd.MNV, gd.NGAYGIAODICH, gd.TIEN, gd.TIENKH, status])
            messagebox.showinfo("Thành công", f"Đã xuất báo cáo ra file: {path}")

        def update_report():
            nonlocal chart_canvas
            # Chỉ phá hủy nội dung trong report_frame
            for widget in report_frame.winfo_children():
                widget.destroy()
            chart_canvas = None

            mkh = entry_mkh.get().strip()
            from_date = entry_from_date.get().strip()
            to_date = entry_to_date.get().strip()
            selected_status = status_filter_var.get()

            transactions = giao_dich_bus.get_giao_dich_all()
            logging.debug(f"Total transactions: {len(transactions)}")

            if mkh:
                try:
                    mkh = int(mkh)
                    transactions = [gd for gd in transactions if gd.MKH == mkh]
                    logging.debug(f"Filtered by MKH={mkh}: {len(transactions)} transactions")
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
                    gd_date_str = str(gd.NGAYGIAODICH)
                    try:
                        gd_date = datetime.strptime(gd_date_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        gd_date = datetime.strptime(gd_date_str, "%Y-%m-%d")
                    
                    if from_date and gd_date.date() < from_date.date():
                        continue
                    if to_date and gd_date.date() > to_date.date():
                        continue
                    if selected_status != "Tất cả":
                        if selected_status == "Thành công" and gd.TT != 1:
                            continue
                        elif selected_status == "Hủy" and gd.TT != 0:
                            continue
                        elif selected_status == "Đang xử lý" and gd.TT != 2:
                            continue
                    filtered_transactions.append(gd)
                except ValueError as e:
                    logging.warning(f"Error parsing date for transaction {gd.MGD}: {str(e)}")
                    continue

            logging.debug(f"Filtered transactions: {len(filtered_transactions)}")
            if not filtered_transactions:
                ctk.CTkLabel(report_frame, text="Không tìm thấy giao dịch phù hợp", font=("Arial", 14), text_color="red").pack(pady=10)
                logging.warning("No transactions found for report")
                return

            status_data = {"Thành công": 0, "Hủy": 0, "Đang xử lý": 0}
            status_amount = {"Thành công": 0, "Hủy": 0, "Đang xử lý": 0}
            for gd in filtered_transactions:
                status_text = {0: "Hủy", 1: "Thành công", 2: "Đang xử lý"}.get(gd.TT, "Không xác định")
                if status_text in status_data:
                    status_data[status_text] += 1
                    status_amount[status_text] += gd.TIEN

            logging.debug(f"Status data: {status_data}")

            top_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
            top_frame.pack(fill="x", pady=5)

            chart_frame = ctk.CTkFrame(report_frame, fg_color="white", corner_radius=10)
            chart_frame.pack(fill="both", pady=5, expand=True)

            summary_frame = ctk.CTkFrame(top_frame, fg_color="white", corner_radius=10)
            summary_frame.pack(fill="x", padx=10, pady=5)

            for status in status_data:
                text = f"{status}: {status_data[status]} giao dịch - Tổng tiền: {status_amount[status]} VND"
                ctk.CTkLabel(summary_frame, text=text, font=("Arial", 14), text_color="#2B2D42").pack(anchor="w", padx=20, pady=2)

            if any(status_data.values()):
                show_chart(status_data, chart_frame)

            ctk.CTkButton(top_frame, text="📄 Xuất CSV", command=lambda: export_csv(filtered_transactions)).pack(pady=5)

            tree_frame = ctk.CTkFrame(report_frame)
            tree_frame.pack(fill="both", expand=True, pady=5)
            style = ttk.Style()
            style.configure("Treeview", font=("Arial", 13), rowheight=28)
            style.configure("Treeview.Heading", font=("Arial", 13, "bold"))

            tree = ttk.Treeview(tree_frame, columns=("MGD", "MKH", "MNV", "NgayGiaoDich", "Tien", "TienKH", "TrangThai"), show="headings")
            for col, title, width in [
                ("MGD", "Mã GD", 70), ("MKH", "Mã KH", 70), ("MNV", "Mã NV", 70),
                ("NgayGiaoDich", "Ngày GD", 140), ("Tien", "Số tiền", 100),
                ("TienKH", "Số dư KH", 100), ("TrangThai", "Trạng thái", 100)
            ]:
                tree.heading(col, text=title)
                tree.column(col, width=width)

            scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            for gd in filtered_transactions:
                status = {0: "Hủy", 1: "Thành công", 2: "Đang xử lý"}.get(gd.TT, "Không xác định")
                tree.insert("", "end", values=(gd.MGD, gd.MKH, gd.MNV, gd.NGAYGIAODICH, gd.TIEN, gd.TIENKH, status))

        # Tạo nút "Tạo báo cáo"
        ctk.CTkButton(form_right, text="📥 Tạo báo cáo", font=("Arial", 14, "bold"), fg_color="#EF233C", command=update_report).pack(pady=10)
        # Gọi update_report lần đầu để hiển thị báo cáo mặc định
        update_report()