from GUI.customerGUI import CustomerApp
import CustomerApp as csTk


# app = csTk.CTk()
# CustomerApp(app)
# app.mainloop()

class CustomerApp:
    def __init__(self, app):
        self.app = app
        self.app.title("Quản lý khách hàng")
        self.app.geometry("500x400")

        self.id_entry = create_entry(self.app, "ID Khách hàng:")
        self.name_entry = create_entry(self.app, "Tên:")
        self.email_entry = create_entry(self.app, "Email:")
        self.phone_entry = create_entry(self.app, "Số điện thoại:")
