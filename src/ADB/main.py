from time import sleep
from ADB.selenium_adb import SeleniumADB
import uiautomator2 as u2
import adbutils

# Kết nối với thiết bị
devices = adbutils.adb.device_list()
if devices:
    device_serial = devices[0].serial
    d = u2.connect(device_serial)
    print(f"Kết nối với thiết bị: {device_serial}")

    # Nhấn nút Home để đảm bảo bạn đang ở màn hình chính
    adb = SeleniumADB()

        # Nhấn nút Home
    adb.press_home()

        # Click vào phần tử với class name là "android.widget.ImageView"
    adb.click_by_text('Bitget Wallet')
    adb.click_by_class("android.widget.ImageView")

        # In thông tin thiết bị
    print(adb.device_info())
else:
    print("Không có thiết bị nào được kết nối.")
