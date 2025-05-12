import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import csv
import logging

logging.basicConfig(level=logging.DEBUG, filename="app.log", filemode="a", format="%(asctime)s - %(levelname)s - %(message)s")

#Hàm báo cáo
def generate_report(frame_right, giao_dich_bus):
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