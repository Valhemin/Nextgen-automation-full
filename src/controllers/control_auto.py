from os import path
from PySide6.QtWidgets import QCheckBox, QTableWidgetItem, QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt
from src.utils import GlobalVariableManager, FileManager

"""Control Auto module"""
class ControlAuto:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance
    
    def __init__(self, main_window) -> None:
        self.main_window = main_window
        self.checkbox_in_list_auto = []
        self.auto_selected = []
        self.global_variable = GlobalVariableManager()
        self.main_window.btn_reload_auto.clicked.connect(self.load_data)
        self.main_window.in_search_auto.textChanged.connect(self.handle_search_auto)
        self.main_window.btn_select_all_auto.clicked.connect(self.handle_select_all_auto)
        self.load_data()

    def load_data(self) -> None:
        list_auto = [
            {'id': 'auto_blum', 'auto_name': 'Auto Blum', "run_async": False, "ready_run": True, "file_data_type": 'txt'},
            {'id': 'auto_timefarm', 'auto_name': 'Auto Timefarm', "run_async": False, "ready_run": True, "file_data_type": 'txt'},
            {'id': 'auto_create_ton_wallet', 'auto_name': 'Auto Create Ton Wallet', "run_async": False, "ready_run": True, "file_data_type": 'txt'},
            {'id': 'auto_get_token_magicnewton', 'auto_name': 'Auto Get Token Magicnewton', "run_async": False, "ready_run": True, "file_data_type": 'txt'},
        ]
        self.global_variable.set_global_list_data_auto(list_auto)
        self.global_variable.set_global_list_data_auto_temp(list_auto)
        self.global_variable.clear_global_auto_selected()
        self.show_data_auto_on_table()
        
    def show_data_auto_on_table(self) -> None:
        try:
            self.auto_selected.clear()
            self.checkbox_in_list_auto.clear()
            self.update_selected_auto_count()
            
            data_auto = self.global_variable.get_global_list_data_auto()
            table = self.main_window.table_list_auto
            table.setRowCount(len(data_auto))

            if len(data_auto) > 0:
                table.setRowCount(len(data_auto))

                for i in range(len(data_auto)):
                    # Add checkbox to table
                    checkbox_in_data_auto = QCheckBox()
                    checkbox_in_data_auto.setChecked(False)
                    checkbox_in_data_auto.stateChanged.connect(self.make_checkbox_state_changed_handler(i, data_auto[i]))
                    if 'checked' in data_auto[i] and data_auto[i]['checked']:
                        checkbox_in_data_auto.setChecked(data_auto[i]['checked'])
                    self.checkbox_in_list_auto.append(checkbox_in_data_auto)

                    widget_checkbox = QWidget()
                    layout_checkbox = QHBoxLayout(widget_checkbox)
                    layout_checkbox.addWidget(checkbox_in_data_auto, alignment=Qt.AlignmentFlag.AlignCenter)
                    layout_checkbox.setContentsMargins(0, 0, 0, 0)

                    # add data to table
                    table.setCellWidget(i, 0, widget_checkbox)
                    table.setItem(i, 1, QTableWidgetItem(data_auto[i]['auto_name']))

                    # Tạo widget cho button và label
                    widget_file_selector = QWidget()
                    layout_file_selector = QHBoxLayout(widget_file_selector)
                    button_get_file = QPushButton("Add File")
                    
                    if 'path_file_data' in data_auto[i] and data_auto[i]['path_file_data']:
                        button_get_file.setText(path.basename(data_auto[i]['path_file_data']))
                    else:
                        # Thêm button để lấy file path
                        button_get_file.setMinimumSize(80, 25)
                    button_get_file.clicked.connect(lambda _, data_auto=data_auto[i], button=button_get_file: self.select_file(data_auto, button))
                    layout_file_selector.addWidget(button_get_file, alignment=Qt.AlignmentFlag.AlignCenter)
                    # Đặt widget vào bảng
                    table.setCellWidget(i, 2, widget_file_selector)  # Cột thứ 3 cho file data in

        except Exception as e:
            print("Error", f"An outer error when show data to table: {e}")
    
    def handle_search_auto(self) -> None:
        data_auto_raw = self.global_variable.get_global_list_data_auto_temp()
        search_text = self.main_window.in_search_auto.text().lower()

        if search_text:
            data_auto_filtered = [auto for auto in data_auto_raw if search_text in auto['auto_name'].lower()]
        else:
            data_auto_filtered = self.global_variable.get_global_list_data_auto_temp()

        self.global_variable.set_global_list_data_auto(data_auto_filtered)
        self.show_data_auto_on_table()
            
    def make_checkbox_state_changed_handler(self, i: int, data: dict) -> callable:
        def handler(state: int) -> None:
            self.checkbox_table_sync_state_changed(state, i, data)
        return handler

    def checkbox_table_sync_state_changed(self, state: int, i: int, data: dict) -> None:
        # 0 == uncheck, 2 == check
        if state == 2:
            if data not in self.auto_selected:
                data['checked'] = True
                self.auto_selected.append(data)
                self.global_variable.set_global_auto_selected(data)
                
        elif state == 0:
            if data in self.auto_selected:
                data['checked'] = False
                self.auto_selected.remove(data)
                self.global_variable.remove_global_auto_selected(data['id'])
        self.update_selected_auto_count()

    def handle_select_all_auto(self) -> None:
        data_auto = self.global_variable.get_global_list_data_auto()
        all_checked = all(checkbox.isChecked() for checkbox in self.checkbox_in_list_auto)

        for i, checkbox in enumerate(self.checkbox_in_list_auto):
            checkbox.setChecked(not all_checked)
            if not all_checked:
                self.checkbox_table_sync_state_changed(2, i, data_auto[i])
            else:
                self.checkbox_table_sync_state_changed(0, i, data_auto[i])

        self.update_selected_auto_count()

    def update_selected_auto_count(self) -> None:
        count_auto_selected = len(self.global_variable.get_global_auto_selected())
        self.main_window.table_list_auto.setHorizontalHeaderItem(0, QTableWidgetItem(f'{count_auto_selected}'))
        self.main_window.btn_run_auto.setEnabled(count_auto_selected > 0)

    def select_file(self, data: dict, button_get_file: QPushButton) -> None:
        file_path = None
        if data.get('file_data_type') == 'txt':
            file_path = FileManager().get_file_path(self.main_window, 'Text files (*.txt)')
        elif data.get('file_data_type') == 'excel':  # Sử dụng elif để tránh kiểm tra không cần thiết
            file_path = FileManager().get_file_path(self.main_window, 'Excel files (*.xlsx *.xls)')
        
        if file_path: 
            data['path_file_data'] = file_path
            file_name = path.basename(file_path)
            button_get_file.setText(file_name)
