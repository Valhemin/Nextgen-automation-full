from src.utils import GlobalVariableManager, random_string

"""Control Generate data module"""
class ControlGenerate:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.main_window.btn_generate_name.clicked.connect(self.handle_generate_full_name)
        self.main_window.btn_generate_mail.clicked.connect(self.handle_generate_mail)
        self.main_window.btn_generate_pass.clicked.connect(self.handle_generate_password)
        self.main_window.btn_generate_address.clicked.connect(self.handle_generate_address)
        self.global_variable = GlobalVariableManager()

    def get_localization(self):
        localization_map = {
            'US': 'en_US',
            'China': 'zh_CN',
            'Germany': 'de',
            'Korea': 'ko',
            'Japan': 'ja',
            'French': 'fr'
        }

        localization = self.main_window.cbb_in_generate_country.currentText()
        return localization_map.get(localization, '')

    def handle_generate_full_name(self):
        country = self.get_localization()
        full_name = random_string.generate_random_full_name(country)
        self.main_window.in_name_generated.setText(full_name)

    def handle_generate_mail(self):
        country = self.get_localization()
        length_mail = self.main_window.in_length_mail.text()
        host_mail = self.main_window.cbb_in_host_mail.currentText()
        if host_mail != 'Custom':
            mail = random_string.generate_random_mail('en_US', length_mail) + host_mail
        else:
            mail = random_string.generate_random_mail('en_US', length_mail)
        self.main_window.in_mail_generated.setText(mail)
        self.global_variable.update_global_config_common({'in_length_mail': length_mail, 'cbb_in_host_mail': host_mail})

    def handle_generate_password(self):
        length_password = self.main_window.in_length_password.text()
        has_special_chars = self.main_window.cb_has_symbols.isChecked()
        password = random_string.generate_random_password(length_password, has_special_chars)
        self.main_window.in_pass_generated.setText(password)
        self.global_variable.update_global_config_common({'in_length_password': length_password, 'cb_has_symbols': has_special_chars})

    def handle_generate_address(self):
        country = self.get_localization()
        address = random_string.generate_random_address(country)
        self.main_window.in_address_generated.setText(address)


