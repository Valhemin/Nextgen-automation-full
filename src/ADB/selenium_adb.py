import uiautomator2 as u2
import adbutils


class SeleniumADB:
    def __init__(self, device_serial=None):
        if not device_serial:
            devices = adbutils.adb.device_list()
            if not devices:
                raise Exception("Không có thiết bị nào được kết nối.")
            device_serial = devices[0].serial

        self.d = u2.connect(device_serial)
        print(f"Kết nối với thiết bị: {device_serial}")

    def start_app(self, package_name):
        """Khởi chạy ứng dụng với package name được cung cấp"""
        self.d.app_start(package_name)

    def stop_app(self, package_name):
        """Dừng ứng dụng với package name được cung cấp"""
        self.d.app_stop(package_name)

    def click_by_text(self, text):
        """Nhấn vào một phần tử dựa trên text"""
        element = self.d.xpath(f'//*[@text="{text}"]')
        if element.exists:
            element.click()
            print(f'Đã click vào "{text}".')
        else:
            print(f'"{text}" không tồn tại trên màn hình.')

    def click_by_class(self, class_name, instance=0):
        """Nhấn vào một phần tử dựa trên class name và instance"""
        element = self.d(className=class_name, instance=instance)
        if element.exists:
            element.click()
            print(f'Đã click vào phần tử với class name "{class_name}" instance {instance}.')
        else:
            print(f'Phần tử với class name "{class_name}" instance {instance} không tồn tại.')

    def click(self, resource_id):
        """Nhấn vào một phần tử dựa trên resource id"""
        self.d(resourceId=resource_id).click()

    def send_keys(self, resource_id, text):
        """Gửi văn bản đến một phần tử dựa trên resource id"""
        self.d(resourceId=resource_id).set_text(text)

    def wait_for_element(self, resource_id, timeout=10):
        """Chờ cho phần tử xuất hiện dựa trên resource id"""
        return self.d(resourceId=resource_id).wait(timeout=timeout)

    def get_element_text(self, resource_id):
        """Lấy văn bản từ một phần tử dựa trên resource id"""
        return self.d(resourceId=resource_id).get_text()

    def screenshot(self, filename):
        """Chụp màn hình và lưu vào file"""
        self.d.screenshot(filename)

    def press_home(self):
        """Nhấn nút Home trên thiết bị"""
        self.d.press('home')

    def device_info(self):
        """In ra thông tin của thiết bị"""
        return self.d.info


# Sử dụng class SeleniumADB

