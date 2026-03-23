import sys
import os
import logging
import webbrowser
import asyncio
from qasync import QEventLoop
from platform import system
from subprocess import Popen
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QHeaderView, QLineEdit, QPushButton, QHBoxLayout
from PySide6.QtGui import QMovie

from src.ui import Ui_MyMainWindow
from src.controllers import ControlGenerate, ControlProfile, ControlAuto, ControlAutoProfile, ControlCommon


class SplashScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle('NextGen Automation Software')
        self.setFixedSize(400, 200)

        layout = QVBoxLayout()
        
        self.title_label = QLabel("NextGen Automation Software")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.title_label)

        self.license_layout = QHBoxLayout()
        
        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("Enter License Key")
        self.license_layout.addWidget(self.license_input)

        self.check_button = QPushButton("Check")
        self.check_button.clicked.connect(self.check_license)
        self.license_layout.addWidget(self.check_button)
        
        self.state_license = QLabel()
        self.state_license.setStyleSheet("font-size: 12px; color: red;")
        layout.addWidget(self.state_license)

        layout.addLayout(self.license_layout)

        self.spinner_label = QLabel()
        layout.addWidget(self.spinner_label, alignment=Qt.AlignmentFlag.AlignCenter)
        movie = QMovie("giphy.gif")  
        self.spinner_label.setMovie(movie)
        movie.start()
        self.spinner_label.setVisible(False) 

        self.link_label = QLabel("Click here for support")
        self.link_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.link_label.mousePressEvent = lambda event: self.open_browser_support()
        layout.addWidget(self.link_label)

        self.setLayout(layout)
        self.check_license()

    def open_browser_support(self):
        webbrowser.open('https://discord.gg/5K7vHxFt')

    def check_license(self):
        license_key = self.license_input.text()
        self.show_spinner(True)
        
        # if self.validate_license(license_key):
        if True:
            asyncio.ensure_future(self.initialize_controllers_and_open_main())
        else:
            self.show_spinner(False)
            self.state_license.setText("Invalid License Key!")
            
    def validate_license(self, license_key: str) -> bool:
        return license_key == "123"

    def show_spinner(self, show: bool):
        self.license_input.setVisible(not show)
        self.check_button.setVisible(not show)
        if not show:
            self.state_license.setText("")  
        self.setFixedSize(400, 300)  
        self.spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner_label.setVisible(show)        

        self.license_layout.addStretch()  
        self.license_layout.addWidget(self.spinner_label)
        self.license_layout.addStretch()

    async def initialize_controllers_and_open_main(self):
        self.main_window.initialize_ui()
        self.main_window.initialize_controllers()
        self.main_window.show()
        self.close()
        
    
class MyMainWindow(QMainWindow, Ui_MyMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def initialize_ui(self):
        self.setWindowTitle('NextGen Automation Software')
        
        fixed_column_index = 0
        self.table_list_auto.setColumnWidth(fixed_column_index, 40)
        self.table_list_profiles.setColumnWidth(fixed_column_index, 40)

        # Lấy số lượng cột tự động
        num_columns_table_auto = self.table_list_auto.columnCount()
        num_columns_table_profile = self.table_list_profiles.columnCount()

        # Đặt các cột còn lại tự động điều chỉnh kích thước
        for i in range(num_columns_table_auto):
            if i != fixed_column_index:
                self.table_list_auto.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        for i in range(num_columns_table_profile):
            if i != fixed_column_index:
                self.table_list_profiles.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        # Disable some elements
        self.btn_stop_auto.setEnabled(False)
        
        # Connect button
        self.lb_lien_he_ho_tro.mousePressEvent = lambda event: self.handle_open_browser_support()
        self.btn_file_data_out.clicked.connect(self.handle_open_file_output)
        
        self.in_date_time_run.setDateTime(QDateTime.currentDateTime())
        
        # Auto Create folder when load app
        folders = ["data"]
        current_directory = os.getcwd()
        for folder in folders:
            if not os.path.exists(os.path.join(current_directory, folder)):
                os.makedirs(folder)
                
    def initialize_controllers(self):
        # Cấu hình cơ bản cho logging
        logging.basicConfig(
            level=logging.INFO,  # Cấp độ log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Định dạng log
            datefmt='%d-%m-%Y %H:%M:%S',  # Định dạng thời gian
            handlers=[
                logging.StreamHandler(),  # Ghi log ra console
                logging.FileHandler(os.path.join(os.getcwd(), 'data', '.app.log'), mode='a', encoding='utf-8')  # Ghi log ra file (append mode)
            ]
        )
        self.control_generate = ControlGenerate(self)
        self.control_profiles = ControlProfile(self)
        self.control_auto = ControlAuto(self)
        self.control_auto_profile = ControlAutoProfile(self)
        self.control_common = ControlCommon(self, control_auto_profile=self.control_auto_profile)
        
    def handle_open_browser_support(self):
        webbrowser.open('https://discord.gg/5K7vHxFt')
        
    def handle_open_file_output(self):
        folder_path = os.path.join(os.getcwd(), 'data')        
        if system() == "Windows":
            os.startfile(folder_path)
        elif system() == "Darwin":  # MacOS
            Popen(["open", folder_path])

    def closeEvent(self, event):
        self.control_common.save_config_on_exit()
        self.control_common.close_all_thread()
        if asyncio.get_event_loop().is_running():
            asyncio.get_event_loop().stop() 
        event.accept()
        QApplication.quit()
    
class MyNextTeam:
    def __init__(self):
        self.app = QApplication(sys.argv)
        # Create a QEventLoop for asyncio integration
        self.loop = QEventLoop(self.app)
        asyncio.set_event_loop(self.loop)
        
        self.main_window = MyMainWindow()
        self.main_window.hide()
        self.splash_screen = SplashScreen(self.main_window)
        self.splash_screen.show()

        self.initialize_app()

    def initialize_app(self):        
        try:
            self.loop.run_forever()
        except Exception as e:
            logging.error(f"Unexpected error: {e}", exc_info=True)
        finally:
            self.loop.close()

if __name__ == "__main__":
    app_instance = MyNextTeam()
    sys.exit(app_instance.app.exec())
