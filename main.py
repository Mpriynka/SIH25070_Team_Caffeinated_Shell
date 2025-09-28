import sys
import os
import uuid
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QTableWidgetItem, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, QTimer

# Import logic modules
from system_info import SystemInfo
from wiping import WipeThread
from certificate import CertificateGenerator


class MainWindow(QMainWindow):
    """Main application window to manage the UI and application flow."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Data Wiper")
        self.ui_files_dir = "ui_files"
        self.user_data = {}
        self.system_data = {}
        self.certificate_id = None

        # Set up the stacked widget to hold all the pages
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.setMinimumSize(850, 600)

        # Load all UI pages
        self.pages = {
            "home": self.load_ui("homepage.ui"),
            "info_input": self.load_ui("info_input_page.ui"),
            "system_info": self.load_ui("system_info_page.ui"),
            "loading": self.load_ui("loading_page.ui"),
            "report": self.load_ui("report_page.ui"),
            "unsuccessful": self.load_ui("unsucessful.ui"),
        }

        # Add pages to the stacked widget
        for page_widget in self.pages.values():
            self.stacked_widget.addWidget(page_widget)

        # Setup connections for each page
        self._setup_home_page()
        self._setup_info_input_page()
        self._setup_system_info_page()
        self._setup_report_page()
        self._setup_unsuccessful_page()
        
        # Initialize helper classes
        self.system_info_handler = SystemInfo()

        # Start on the home page
        self.go_to_page("home")

    def load_ui(self, filename):
        """Loads a .ui file and returns the widget."""
        path = os.path.join(self.ui_files_dir, filename)
        ui_file = QFile(path)
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Cannot open {filename}: {ui_file.errorString()}")
            sys.exit(-1)
        loader = QUiLoader()
        widget = loader.load(ui_file, self)
        ui_file.close()
        return widget

    def go_to_page(self, page_name):
        """Switches the stacked widget to the specified page."""
        widget = self.pages.get(page_name)
        if widget:
            self.stacked_widget.setCurrentWidget(widget)
        else:
            print(f"Error: Page '{page_name}' not found.")

    def _setup_home_page(self):
        """Set up signals and slots for the homepage."""
        home_page = self.pages["home"]
        home_page.Laptop_pushButton.clicked.connect(lambda: self.go_to_page("info_input"))
        # Android button can be disabled or show a message
        home_page.Android_pushButton.clicked.connect(self._android_not_supported)

    def _setup_info_input_page(self):
        """Set up signals and slots for the info input page."""
        info_page = self.pages["info_input"]
        info_page.pushButton.clicked.connect(self._collect_user_info)

        # Enable 'Continue' button only when essential fields are filled
        required_fields = [
            info_page.Name_lineEdit,
            info_page.OrganizationlineEdit,
            info_page.AssetTag_lineEdit,
        ]
        for field in required_fields:
            field.textChanged.connect(lambda: self._validate_info_input(required_fields))

    def _setup_system_info_page(self):
        """Set up signals and slots for the system info page."""
        sys_info_page = self.pages["system_info"]
        sys_info_page.Home_Button.clicked.connect(lambda: self.go_to_page("home"))
        sys_info_page.RefreshDevices_Button.clicked.connect(self.populate_device_table)
        sys_info_page.Wipe_Button.clicked.connect(self.start_wiping_process)
        
        # Setup table
        table = sys_info_page.tableWidget
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Device Name", "Model", "Serial Number", "Size"])
        table.setColumnWidth(0, 150)
        table.setColumnWidth(1, 250)
        table.setColumnWidth(2, 200)
        table.setColumnWidth(3, 100)


    def _setup_report_page(self):
        """Set up signals and slots for the report page."""
        report_page = self.pages["report"]
        report_page.Home_Button.clicked.connect(lambda: self.go_to_page("home"))
        # Download and Print buttons would need platform-specific logic
        report_page.Download_Button.clicked.connect(self._show_download_info)

    def _setup_unsuccessful_page(self):
        """Set up signals and slots for the unsuccessful page."""
        unsuccessful_page = self.pages["unsuccessful"]
        unsuccessful_page.pushButton.clicked.connect(lambda: self.go_to_page("system_info"))


    def _android_not_supported(self):
        """Shows a message that Android is not yet supported."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("Android Support")
        msg_box.setInformativeText("Wiping for Android devices is not yet implemented.")
        msg_box.setWindowTitle("Information")
        msg_box.exec()

    def _validate_info_input(self, fields):
        """Check if all required fields on the info page are filled."""
        info_page = self.pages["info_input"]
        is_valid = all(field.text().strip() for field in fields)
        info_page.pushButton.setEnabled(is_valid)
        
    def _collect_user_info(self):
        """Collects data from the info input form and proceeds."""
        info_page = self.pages["info_input"]
        self.user_data = {
            "name": info_page.Name_lineEdit.text(),
            "organization": info_page.OrganizationlineEdit.text(),
            "title": info_page.Title_lineEdit.text(),
            "location": info_page.Email_lineEdit.text(), # Assuming this is location
            "phone": info_page.Phone_lineEdit.text(),
            "media_property_number": info_page.AssetTag_lineEdit.text(),
            "source": info_page.Source_lineEdit.text(),
            "backup_location": info_page.Backup_lineEdit.text(),
            "notes": info_page.Notes_lineEdit.text(),
            "destination": info_page.Destination_lineEdit.text()
        }
        self.populate_device_table()
        self.go_to_page("system_info")

    def populate_device_table(self):
        """Fetches storage device info and populates the table."""
        sys_info_page = self.pages["system_info"]
        table = sys_info_page.tableWidget
        table.setRowCount(0)  # Clear existing rows

        self.system_data = self.system_info_handler.get_all_info()
        devices = self.system_data.get("storage_devices", [])

        for row_num, device in enumerate(devices):
            table.insertRow(row_num)
            table.setItem(row_num, 0, QTableWidgetItem(device.get("name", "N/A")))
            table.setItem(row_num, 1, QTableWidgetItem(device.get("model", "N/A")))
            table.setItem(row_num, 2, QTableWidgetItem(device.get("serial", "N/A")))
            table.setItem(row_num, 3, QTableWidgetItem(device.get("size", "N/A")))
            
    def start_wiping_process(self):
        """Initiates the wiping thread for all detected devices."""
        self.certificate_id = str(uuid.uuid4())
        
        # Show a confirmation dialog with the UUID
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText("Are you sure you want to proceed with wiping?")
        msg_box.setInformativeText(f"This action is IRREVERSIBLE.\n\nYour certificate reference ID will be:\n{self.certificate_id}")
        msg_box.setWindowTitle("Confirm Wipe")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        if msg_box.exec() == QMessageBox.Yes:
            self.go_to_page("loading")
            # This is where you would get the list of devices to wipe
            devices_to_wipe = [dev['name'] for dev in self.system_data.get("storage_devices", [])]
            
            # For now, we simulate wiping one device. In a real app, you might loop or have selections.
            # Using a placeholder path for simulation.
            simulated_device_path = "wipe_simulation.tmp"

            self.wipe_thread = WipeThread(simulated_device_path)
            self.wipe_thread.progress.connect(self.update_loading_progress)
            self.wipe_thread.finished.connect(self.on_wiping_finished)
            self.wipe_thread.start()

    def update_loading_progress(self, value):
        """Updates the progress bar on the loading page."""
        loading_page = self.pages["loading"]
        loading_page.progressBar.setValue(value)

    def on_wiping_finished(self, success, message, report_data):
        """Handles the completion of the wiping process."""
        if success:
            cert_generator = CertificateGenerator(
                user_data=self.user_data,
                system_data=self.system_data,
                wipe_report=report_data,
                certificate_id=self.certificate_id
            )
            cert_generator.generate_all()
            
            report_page = self.pages["report"]
            report_page.ReID_Label.setText(f"Ref. ID: {self.certificate_id}")
            self.go_to_page("report")
        else:
            print(f"Wiping failed: {message}")
            self.go_to_page("unsuccessful")
            
    def _show_download_info(self):
        """Shows where the report files are saved."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("Reports Generated")
        msg_box.setInformativeText(f"Certificate files (PDF and JSON) have been saved in the application's root directory with the ID:\n{self.certificate_id}")
        msg_box.setWindowTitle("Download Information")
        msg_box.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
