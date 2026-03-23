from PySide6.QtWidgets import QMessageBox, QCheckBox, QTableWidgetItem, QWidget, QHBoxLayout
from PySide6.QtCore import Qt
from src.utils import GlobalVariableManager
from src.apis import GPMLoginAPI

"""Control Profile module"""

class ControlProfile:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance
    
    def __init__(self, main_window: any) -> None:
        self.main_window = main_window
        self.checkbox_in_list_profiles: list[QCheckBox] = []
        self.profiles_selected: list[dict] = []
        self.index_group: int = 1
        self.group_selected: str = 'All'
        self.data_groups: list[dict] | None = None
        self.api_url: str = self.get_api_url() 
        self.gpm_api = GPMLoginAPI(self.api_url)
        self.global_variable = GlobalVariableManager()

        self.main_window.btn_reload_profiles.clicked.connect(self.load_data)
        self.main_window.btn_select_all_profiles.clicked.connect(self.handle_select_all_profiles)
        self.main_window.in_search_profiles.textChanged.connect(self.handle_search_profiles)
        self.main_window.cb_groups_profile.currentIndexChanged.connect(self.handle_change_groups_profile)

        self.show_data_groups_on_cb()
        self.load_data()
            
    def show_data_groups_on_cb(self) -> None:
        self.data_groups = self.gpm_api.get_groups()
        self.main_window.cb_groups_profile.clear()
        if self.data_groups:
            for group in self.data_groups:
                self.main_window.cb_groups_profile.addItem(group['name'])

    def load_data(self) -> None:
        self.api_url = self.get_api_url() 
        if self.data_groups:
            selected_group = next((group for group in self.data_groups if (group['name']).lower() == self.group_selected.lower()), None)
            self.index_group = selected_group['id'] if selected_group else 1
        data_profile = self.gpm_api.get_profiles(groupId=self.index_group, newApiUrl=self.api_url)
        self.global_variable.set_global_list_data_profiles(data_profile)
        self.global_variable.set_global_list_data_profiles_temp(data_profile)
        self.global_variable.clear_global_profiles_selected()
        self.show_data_profiles_on_table()

    def show_data_profiles_on_table(self) -> None:
        try:
            self.checkbox_in_list_profiles.clear()
            self.profiles_selected.clear()
            self.update_selected_profiles_count()
            
            data_profiles = self.global_variable.get_global_list_data_profiles()
            table = self.main_window.table_list_profiles
            table.setRowCount(len(data_profiles))

            for i, profile in enumerate(data_profiles):
                checkbox = QCheckBox()
                checkbox.setChecked(False)
                checkbox.stateChanged.connect(self.make_checkbox_state_changed_handler(i, profile))
                self.checkbox_in_list_profiles.append(checkbox)

                widget_checkbox = QWidget()
                layout_checkbox = QHBoxLayout(widget_checkbox)
                layout_checkbox.addWidget(checkbox, alignment=Qt.AlignmentFlag.AlignCenter)
                layout_checkbox.setContentsMargins(0, 0, 0, 0)

                table.setCellWidget(i, 0, widget_checkbox)
                table.setItem(i, 1, QTableWidgetItem(profile['name']))
                # table.setItem(i, 2, QTableWidgetItem(data_profiles[i]['profile_id']))
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", "Vui lòng kiểm tra xem GPMLogin đã được mở chưa.")
            print("Lỗi", f"Đã xảy ra lỗi khi hiển thị dữ liệu lên bảng: {e}")
            
    def handle_change_groups_profile(self) -> None:
        self.group_selected = self.main_window.cb_groups_profile.currentText()
        self.load_data()

    def handle_search_profiles(self) -> None:
        data_profile_raw = self.global_variable.get_global_list_data_profiles_temp()
        search_text = self.main_window.in_search_profiles.text().lower().strip()  # Loại bỏ khoảng trắng

        if search_text:
            # Tìm kiếm với điều kiện cho phép tìm kiếm gần đúng
            data_profile_filtered = [profile for profile in data_profile_raw if search_text in profile['name'].lower() or profile['name'].lower().startswith(search_text)]
        else:
            data_profile_filtered = self.global_variable.get_global_list_data_profiles_temp()

        self.global_variable.set_global_list_data_profiles(data_profile_filtered)
        self.show_data_profiles_on_table()
 
    def make_checkbox_state_changed_handler(self, i: int, data: dict) -> callable:
        def handler(state: int) -> None:
            self.checkbox_table_sync_state_changed(state, i, data)
        return handler

    def checkbox_table_sync_state_changed(self, state: int, i: int, data: dict) -> None:
        # 0 == uncheck, 2 == check
        if state == 2:
            if data not in self.profiles_selected:
                self.profiles_selected.append(data)
                self.global_variable.set_global_profiles_selected(data)  

        elif state == 0:
            if data in self.profiles_selected:
                self.profiles_selected.remove(data)
                self.global_variable.remove_global_profiles_selected(data['id'])
        
        self.update_selected_profiles_count()

    def handle_select_all_profiles(self) -> None:
        data_profiles = self.global_variable.get_global_list_data_profiles()
        all_checked = all(checkbox.isChecked() for checkbox in self.checkbox_in_list_profiles)
        for i, checkbox in enumerate(self.checkbox_in_list_profiles):
            checkbox.setChecked(not all_checked)
            if not all_checked:
                self.checkbox_table_sync_state_changed(2, i, data_profiles[i])
            else:
                self.checkbox_table_sync_state_changed(0, i, data_profiles[i])

        self.update_selected_profiles_count()

    def update_selected_profiles_count(self) -> None:
        count_profile_selected = len(self.global_variable.get_global_profiles_selected())
        self.main_window.table_list_profiles.setHorizontalHeaderItem(0, QTableWidgetItem(f'{count_profile_selected}'))
        self.main_window.btn_run_auto.setEnabled(count_profile_selected > 0)

    def get_api_url(self) -> str:
        return self.main_window.in_api_url.text() if self.main_window.in_api_url.text() else 'http://127.0.0.1:19995'
