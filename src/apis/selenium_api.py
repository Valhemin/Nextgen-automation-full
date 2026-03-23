from selenium.common import *
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.remote.webelement import WebElement

# import cv2
# import numpy as np
# from PIL import Image
# from io import BytesIO

from typing import Literal, Tuple, Optional, Any
import pyperclip
import requests
import time
from .headers import headers

class SeleniumAPI(object):
    def __init__(
        self,
        driver: webdriver.Chrome,
        custom_headers: dict | None = None,
        wait_time: float = 10.0,
    ):
        self.driver = driver
        self.action = ActionChains(self.driver)
        self.default_headers = headers
        self.default_wait_element_time = wait_time
        if custom_headers:
            self.default_headers.update(custom_headers)
        self.get_user_agent()

    def detect_locator_type(self, locator: str) -> Tuple[str, str]:
        # Case 1: Detect if the locator is XPath
        if (
            locator.startswith("//")
            or locator.startswith("(")
            or "@" in locator
            or locator.startswith(".//")
        ):
            return By.XPATH, locator

        # Case 2: Detect if the locator is CSS Selector
        elif (
            locator.startswith("#")
            or locator.startswith(".")
            or locator.startswith("[")
            or locator.startswith("root")
        ):
            return By.CSS_SELECTOR, locator

        # Case 3: Detect if the locator is an ID
        elif locator.startswith("id="):
            return By.ID, locator[3:]

        # Case 4: Detect if the locator is a Class Name
        elif locator.startswith("class="):
            return By.CLASS_NAME, locator[6:]

        # Case 5: Detect if the locator is a Tag Name
        elif locator.isidentifier():  # Kiểm tra nếu là tên hợp lệ
            return By.TAG_NAME, locator

        # Case 6: Detect if the locator is a Link Text or Partial Link Text
        elif locator.startswith("link="):
            return By.LINK_TEXT, locator[5:]
        elif locator.startswith("partial_link="):
            return By.PARTIAL_LINK_TEXT, locator[13:]

        # Case 7: If it's plain text, assume it's to find an element by its text content
        else:
            return By.XPATH, f"//*[contains(text(), '{locator}')]"

    def find_element_with_wait(self, locator: str, timeout: float | None = None) -> WebElement:
        wait_time = timeout or self.default_wait_element_time
        locator_type, processed_locator = self.detect_locator_type(locator)
        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((locator_type, processed_locator))
            )
        except TimeoutException:
            print(f"Không tìm thấy phần tử '{locator}' sau {wait_time} giây.")
            raise
        except Exception as e:
            print(f"Lỗi khi tìm phần tử '{locator}': {str(e)}")
            raise
        
    def wait_element(self, locator: str, timeout: float | None = None):
        wait_time = timeout or self.default_wait_element_time
        locator_type, processed_locator = self.detect_locator_type(locator)
        WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located((locator_type, processed_locator))
        )
        
    def sleep(self, delay: float = 1):
        time.sleep(delay)

    """
    Create a Action Handler
    """

    def click_element(self, locator: str | None = None, delay: float = 1) -> bool:
        if locator is not None:
            try:
                element = self.find_element_with_wait(locator)
                element.click()
                time.sleep(delay)
                return True
            except Exception as e:
                print(f"Không thể click element '{locator}'. Lỗi: {e}")
                return False
        else:
            self.action.click().perform()

    def touch_element(
        self,
        locator: str,
        is_tap_random: bool = False,
        num_position_tap: int = 1,
        tap_count: int = 100,
        time_limit: int | None = None,
        delay: float = 1
    ) -> bool:
        """Nếu tap_count được truyền, hàm sẽ đếm số lần chạm và dừng khi đạt số lượng tap_count.
        Nếu chỉ có time_limit (ms), hàm sẽ chạm liên tục với khoảng cách giữa các lần chạm là 0 - 300ms cho đến khi hết thời gian time_limit.
        Nếu cả hai đều được truyền, hàm sẽ dừng khi đạt một trong hai điều kiện (đủ số lần chạm hoặc hết thời gian).
        Num position tap ý chỉ số vị trí chạm, mặc định là 1
        """
        try:
            script = f"""
            function eventTouch(element, isTapRandom, numPositionTap, tapCount, timeLimit) {{
            function createTouch(element, x, y) {{
                return new Touch({{
                    identifier: Date.now(),
                    target: element,
                    clientX: x,
                    clientY: y,
                    pageX: x + window.scrollX,
                    pageY: y + window.scrollY,
                    screenX: x + window.screenX,
                    screenY: y + window.screenY,
                }});
            }}

            function triggerTouch(element, x, y) {{
                const touch = createTouch(element, x, y);

                const touchEventStart = new TouchEvent("touchstart", {{
                    bubbles: true,
                    cancelable: true,
                    touches: [touch],
                    targetTouches: [touch],
                    changedTouches: [touch],
                }});

                element.dispatchEvent(touchEventStart);

                const touchEventEnd = new TouchEvent("touchend", {{
                    bubbles: true,
                    cancelable: true,
                    touches: [],
                    targetTouches: [],
                    changedTouches: [touch],
                }});

                element.dispatchEvent(touchEventEnd);
            }}

            function getRandomPosition(element) {{
                const rect = element.getBoundingClientRect();
                let x = rect.left + rect.width / 2;
                let y = rect.top + rect.height / 2;
                if (isTapRandom) {{
                    x = rect.left + Math.random() * rect.width;
                    y = rect.top + Math.random() * rect.height;
                }}
                return {{ x, y }};
            }}

            function tap(element, numPositionTap, tapCount, timeLimit ) {{
                const startTime = Date.now();
                let taps = 0;

                function performTap() {{
                    if (tapCount && taps >= tapCount) {{
                        return;
                    }}

                    if (timeLimit && (Date.now() - startTime) >= timeLimit) {{
                        return;
                    }}

                    // Perform taps with random positions
                    for (let i = 0; i < numPositionTap; i++) {{
                        const {{ x, y }} = getRandomPosition(element);
                        triggerTouch(element, x, y);  // Trigger touch at a new random position each time
                    }}

                    taps += 1;

                    // Random delay between 0 and 300ms
                    const randomDelay = Math.floor(Math.random() * 300);

                    setTimeout(performTap, randomDelay);
                }}

                performTap();
            }}

            if (element) {{
                tap(element, numPositionTap, tapCount, timeLimit );
            }}
            }}
        
            eventTouch({element}, {is_tap_random}, {num_position_tap}, {tap_count}, {time_limit});
            """
            if time_limit is not None:
                time_limit = time_limit * 1000
            # Tìm phần tử để thực hiện chạm
            element = self.find_element_with_wait(locator)
            self.driver.execute_script(script)
            time.sleep(delay)
            return True
            
        except Exception as e:
            print(f"Không tìm thấy element {locator} để touch. Error: {e}")
            return False

    def mouse_press_hold_with_delay(self, locator: str, hold_time: float = 2.0, delay: float = 1) -> bool:
        try:
            element = self.find_element_with_wait(locator)
            self.action.click_and_hold(on_element=element).perform()

            # Chờ trong thời gian hold_time trước khi thả ra
            time.sleep(hold_time)

            # Thả ra
            self.action.release().perform()
            time.sleep(delay)
            return True
        except Exception as e:
            print(f"Không tìm thấy element {locator} để mouse press hold with delay. Error: {e}")
            return False

    def mouse_move_to_element(self, locator: str, delay: float = 1) -> bool:
        try:
            element = self.find_element_with_wait(locator)
            self.action.move_to_element(element).perform()
            time.sleep(delay)
            return True
        except Exception as e:
            print(f"Không tìm thấy element {locator} để mouse move to element.  Error: {e}")
            return False

    def mouse_move_by_offset(self, x: int = 0, y: int = 0) -> None:
        self.action.move_by_offset(x, y).perform()

    def press_and_hold_key(self, key: str, duration: float = 0.2, delay: float = 1) -> None:
        valid_keys = {
            "SHIFT": Keys.SHIFT, "CONTROL": Keys.CONTROL, "ALT": Keys.ALT, "TAB": Keys.TAB,
            "ENTER": Keys.ENTER, "BACKSPACE": Keys.BACKSPACE, "DELETE": Keys.DELETE,
            "ESCAPE": Keys.ESCAPE, "SPACE": Keys.SPACE,
            "PAGE_UP": Keys.PAGE_UP, "PAGE_DOWN": Keys.PAGE_DOWN, "END": Keys.END, "HOME": Keys.HOME,
            "LEFT": Keys.LEFT, "UP": Keys.UP, "RIGHT": Keys.RIGHT, "DOWN": Keys.DOWN,
            "INSERT": Keys.INSERT,
            "F1": Keys.F1, "F2": Keys.F2, "F3": Keys.F3, "F4": Keys.F4, "F5": Keys.F5, "F6": Keys.F6,
            "F7": Keys.F7, "F8": Keys.F8, "F9": Keys.F9, "F10": Keys.F10, "F11": Keys.F11, "F12": Keys.F12
        }
        actual_key = valid_keys[key]
        self.action.key_down(actual_key).perform()
        time.sleep(duration)
        self.action.key_up(actual_key).perform()
        time.sleep(delay)
        
    def type_text(self, locator: str, text: str, delay: float = 0.2) -> bool:
        try:
            element = self.find_element_with_wait(locator)
            element.click()  # Đảm bảo phần tử được chọn
            for char in text:
                element.send_keys(char)
                time.sleep(delay)
            time.sleep(1)
            return True
        except Exception as e:
            print(f"Không thể nhập văn bản vào phần tử '{locator}'. Lỗi: {e}")
            return False

    def clear_text(self, locator: str, delay: float = 1) -> bool:
        try:
            element = self.find_element_with_wait(locator)
            element.clear()
            time.sleep(delay)
            return True
        except Exception as e:
            print(f"Không thể xóa văn bản từ phần tử '{locator}'. Lỗi: {e}")
            return False

    def scroll_to_element(self, locator: str, delay: float = 1) -> bool:
        try:
            element = self.find_element_with_wait(locator)
            self.action.scroll_to_element(element).perform()
            time.sleep(delay)
            return True
        except Exception as e:
            print("Không tìm thấy element để scroll to element. Error: {e}")
            return False

    def scroll_by_amount(self, delta_x=0, delta_y=0, delay: float = 1) -> None:
        self.action.scroll_by_amount(delta_x, delta_y).perform()
        time.sleep(delay)

    """
    Creates a new Elements Handler
    """

    def element_is_exist(self, locator: str, duration: float | None = None) -> bool:
        try:
            self.find_element_with_wait(locator, timeout=duration)
            return True
        except TimeoutException:
            return False
        except Exception:
            return False

    def get_text(self, locator: str) -> str | None:
        try:
            element = self.find_element_with_wait(locator)
            return element.text
        except Exception as e:
            print(f"Không thể lấy văn bản từ phần tử '{locator}'. Lỗi: {e}")
            return None

    def get_attribute(self, locator: str, attribute: str) -> str | None:
        try:
            element = self.find_element_with_wait(locator)
            return element.get_attribute(attribute)
        except Exception as e:
            print(f"Không thể lấy thuộc tính '{attribute}' từ phần tử '{locator}'. Lỗi: {e}")
            return None

    def get_number_of_elements(self, locator: str) -> int:
        try:
            element = self.find_element_with_wait(locator)
            return len(element.find_elements(By.XPATH, "ancestor::*"))
        except Exception as e:
            print(
                f"Không tìm thấy element {locator} để get number of element. Error: {e}"
            )
            return 0
    
    def get_cookie(self, cookie_name: str | None = None) -> dict | None:
        return self.driver.get_cookie(cookie_name)

    def select_dropdown(self, locator: str, delay: float = 1) -> Select | None:
        try:
            element = self.find_element_with_wait(locator)
            dropdown = Select(element)
            time.sleep(delay)
            return dropdown
        except Exception as e:
            print(f"Không tìm thấy element {locator} để select dropdown. Error: {e}")
            return None
            
    def copy_to_clipboard(self, text) -> None:
        pyperclip.copy(text)
        
    def paste_from_clipboard(self, text: str = None, locator: str = None, delay: float = 1) -> str | None:
        try:
            if text is not None:
                pyperclip.copy(text)
                
            # Nên truyền locator vào nếu muốn thực hiện past còn không truyền sẽ thực hiện lấy nội dung trong clipboard, lấy nội dung thường phù hợp trong trường hợp lấy mã pharse khi tạo ví
            if locator is not None:
                element = self.find_element_with_wait(locator)
                element.send_keys(Keys.CONTROL + "v")
            time.sleep(delay)    
            return pyperclip.paste()
        except Exception as e:
            print(f"Không thể paste từ clipboard. Error: {e}")
            return None

    """
    Create a Navigation Handler
    """

    def new_tab(self, url: str = '', timeout: float = 40.0) -> None:
        # Bắt đầu đo thời gian tải trang
        start_time = time.time()
        # Mở một tab mới với URL đã cho
        self.driver.execute_script(f"window.open('{url}', '_blank');")

        # Chuyển sang tab mới mở
        self.driver.switch_to.window(self.driver.window_handles[-1])

        # Đi cho đến khi trang được tải hoàn toàn
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "interactive" or driver.execute_script("return document.readyState") == "complete"
        )
        # Tính thời gian tải trang
        end_time = time.time()
        load_time = end_time - start_time
        self.default_wait_element_time = load_time + 5

    def close_tab(self, index: Optional[int] = None, delay: float = 1) -> None:
        try:
            handles = self.driver.window_handles
            num_tabs = len(handles)

            if index is not None:
                # Chuyển chỉ số từ 1 sang 0 index bắt đầu từ 1
                adjusted_index = index - 1
                
                if 0 <= adjusted_index < num_tabs:
                    # Lưu tab hiện tại
                    current_handle = self.driver.current_window_handle
                    
                    # Chuyển sang tab theo chỉ số đã điều chỉnh và đóng nó
                    self.driver.switch_to.window(handles[adjusted_index])
                    self.driver.close()

                    # Cập nhật danh sách tab còn lại sau khi đóng
                    remaining_handles = self.driver.window_handles

                    if remaining_handles:
                        # Chuyển về tab trước đó
                        if current_handle in remaining_handles:
                            self.driver.switch_to.window(current_handle)
                        else:
                            self.driver.switch_to.window(remaining_handles[0])
                    else:
                        print("Không còn tab nào sau khi đóng tab được chỉ định.")
                else:
                    print(f"Index {index} không hợp lệ. Có {num_tabs} tab đang mở.")
            else:
                if num_tabs <= 1:
                    return
                else:
                    # Đóng tất cả các tab ngoại trừ tab đầu tiên
                    for i in range(num_tabs - 1, 0, -1):
                        self.driver.switch_to.window(handles[i])
                        self.driver.close()

                    # Chuyển về tab đầu tiên
                    self.driver.switch_to.window(handles[0])
            
            time.sleep(delay)
        except Exception as e:
            print(f"Lỗi khi đóng tab. Error: {e}")

    def open_URL(self, url: str = 'https://www.google.com', timeout: float = 40.0) -> None:
        # Bắt đầu đo thời gian tải trang
        start_time = time.time()
        self.driver.get(url)
        
        # Đợi cho đến khi trang được tải hoàn toàn dựa vào DOMContentLoaded
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "interactive" or driver.execute_script("return document.readyState") == "complete"
        )
        # Tính thời gian tải trang
        end_time = time.time()
        load_time = end_time - start_time
        self.default_wait_element_time = load_time + 5

    def get_URL(self) -> str:
        return self.driver.current_url

    def active_tab(self, index: int = 0, delay: float = 1) -> None:
        self.driver.switch_to.window(self.driver.window_handles[index])
        time.sleep(delay)

    def get_all_tabs(self) -> list:
        return self.driver.window_handles

    def go_back(self, delay: float = 1) -> None:
        self.driver.back()
        time.sleep(delay)

    def go_forward(self, delay: float = 1) -> None:
        self.driver.forward()
        time.sleep(delay)

    def refresh(self, delay: float = 1) -> None:
        self.driver.refresh()
        time.sleep(delay)

    def switch_to_iframe(self, locator: str = 'iframe', delay: float = 1) -> bool:
        try:
            element = self.find_element_with_wait(locator)
            self.driver.switch_to.frame(element)
            time.sleep(delay)
            return True
        except Exception as e:
            print(f"Không tìm thấy element {locator} để switch frame. Error: {e}")
            return False

    def switch_to_default_content(self, delay: float = 1) -> None:
        self.driver.switch_to.default_content()
        time.sleep(delay)

    def switch_to_popup(self, delay: float = 1) -> bool:
        try:
            original_window = self.driver.current_window_handle
            new_window = [
                window
                for window in self.driver.window_handles
                if window != original_window
            ][0]
            self.driver.switch_to.window(new_window)
            time.sleep(delay)
            return True
        except Exception as e:
            print(f"Lỗi khi switch popup. Error: {e}")
            return False

    def maximize_window(self, delay: float = 1) -> None:
        self.driver.maximize_window()
        time.sleep(delay)

    def fullscreen_window(self, delay: float = 1) -> None:
        self.driver.fullscreen_window()
        time.sleep(delay)

    def minimize_window(self, delay: float = 1) -> None:
        self.driver.minimize_window()
        time.sleep(delay)

    def set_window_size(self, width: int, height: int, delay: float = 1) -> None:
        self.driver.set_window_size(width, height)
        time.sleep(delay)

    def get_window_size(self) -> tuple:
        return self.driver.get_window_size()

    def get_window_position(self) -> tuple:
        return self.driver.get_window_position()

    def set_window_position(self, x: int, y: int, delay: float = 1) -> None:
        self.driver.set_window_position(x, y)
        time.sleep(delay)
        
    def accept_alert(self, delay: float = 1) -> bool:
        try:
            alert = Alert(self.driver)
            alert.accept()
            time.sleep(delay)
            return True
        except Exception as e:
            print(f"Không có alert để xử lý. Error: {e}")
            return False

    def dismiss_alert(self, delay: float = 1) -> bool:
        try:
            alert = Alert(self.driver)
            alert.dismiss()
            time.sleep(delay)
            return True
        except Exception as e:
            print(f"Không có alert để xử lý. Error: {e}")
            return False

    """
    Create handle File
    """

    def upload_file(self, locator: str, file_path: str, delay: float = 2) -> bool:
        try:
            # Tìm phần tử input file
            element = self.find_element_with_wait(locator)
            # Chọn tệp để tải lên
            element.send_keys(file_path)
            time.sleep(delay)
            return True
        except Exception as e:
            print(f"Không tìm thấy element {locator} để upload file. Error: {e}")
            return False

    def download_image(
        self, image_url: str = "", locator: str = "", save_path: str = ""
    ) -> bool:
        try:
            if locator != "":
                element = self.find_element_with_wait(locator)
                image_url = element.get_attribute("src")

            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                with open(save_path, "wb") as file:
                    file.write(response.content)
                print(f"Ảnh đã được lưu vào {save_path}")
                return True
            else:
                print(f"Lỗi tải ảnh: {response.status_code}")
                return False

        except Exception as e:
            print(f"Không tìm thấy element {locator} để download image. Error: {e}")
            return False

    """
    Create handle JavaScript
    """

    def get_query_id(self, type_get: Literal["full", "partial", "decode"] = "partial") -> str | None:
        element = self.find_element_with_wait("iframe")

        if type_get == "full":
            script = """
            const iframe = document.querySelector("iframe")?.src;
            if (iframe) {
                return iframe;
            } else {
                console.log("Iframe not found.");
                return "";
            }
            """
            return self.driver.execute_script(script)

        elif type_get == "partial":
            script = """
            const iframe = document.querySelector("iframe");
            if (iframe) {
                const url = new URL(iframe.src);
                const params = new URLSearchParams(url.hash.substring(1)); // Get parameters from hash
                const tgWebAppData = params.get("tgWebAppData");
                if (tgWebAppData) {
                    return tgWebAppData;
                } else {
                    console.log("tgWebAppData not found.");
                    return "";
                }
            } else {
                console.log("Iframe not found.");
                return "";
            }
            """
            return self.driver.execute_script(script)

        elif type_get == "decode":
            script = """
            const iframeSrc = document.querySelector("iframe")?.src;
            console.log(iframeSrc);
            if (iframeSrc) {
                const match = iframeSrc.match(/tgWebAppData=([^&]*)/);
                if (match) {
                    let decodedString = decodeURIComponent(decodeURIComponent(match[1]));
                    decodedString = encodeURI(decodedString).replaceAll("&", "%26");
                    return decodedString;
                } else {
                    console.log("tgWebAppData not found in the iframe src.");
                    return "";
                }
            } else {
                console.log("Iframe not found.");
                return "";
            }
            """
            return self.driver.execute_script(script)
        return None

    def get_user_agent(self) -> str | None:
        # Nhớ gọi hàm này nếu như muốn tự động update User-Agent trong default headers
        user_agent = self.driver.execute_script("return navigator.userAgent")
        if user_agent:
            self.default_headers["User-Agent"] = user_agent

            if "Android" in user_agent:
                self.default_headers.update(
                    {"Sec-Ch-Ua-Mobile": "?1", "Sec-Ch-Ua-Platform": '"Android"'}
                )
            # Kiểm tra nếu chuỗi 'User-Agent' chứa chữ 'iPhone'
            elif "iPhone" in user_agent:
                self.default_headers.update(
                    {"Sec-Ch-Ua-Mobile": "?1", "Sec-Ch-Ua-Platform": '"iOS"'}
                )
            # Kiểm tra nếu chuỗi 'User-Agent' chứa chữ 'Windows'
            elif "Windows" in user_agent:
                self.default_headers.update(
                    {"Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": '"Windows"'}
                )
            # Kiểm tra nếu chuỗi 'User-Agent' chứa chữ 'Windows'
            elif "Macintosh" in user_agent:
                self.default_headers.update(
                    {"Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": '"macOS"'}
                )

            return user_agent
        else:
            return None

    def update_headers(self, custom_headers: dict) -> None:
        """
        Cập nhật headers mặc định với headers tùy chỉnh.

        :param headers: Headers tùy chỉnh.
        """
        self.default_headers.update(custom_headers)

    # execute get method request on browser
    def get_request(self, url: str, params: dict | None = None) -> Any:
        # Đây là một hàm đồng bộ, nó dùng trong trường hợp muốn chạy và python sẽ dừng chờ kết quả trả về
        default_headers = self.default_headers.copy()
        params_js = f"new URLSearchParams({params}).toString()" if params else "''"

        script = f"""
        const url = new URL('{url}');
        url.search = {params_js};
        return fetch(url.toString(), {{
            method: 'GET',
            headers: f"{default_headers}"
        }}).then(response => {{
            return response.json();
        }}).catch(error => {{
            return {{ error: error.message }};
        }});
        """
        return self.driver.execute_script(script)

    # execute post method request on browser
    def post_request(self, url: str, data: dict = {}) -> Any:
        # Đây là một hàm đồng bộ, nó dùng trong trường hợp muốn chạy và python sẽ dừng chờ kết quả trả về
        default_headers = self.default_headers.copy()
        default_headers["Content-Type"] = "application/json"

        script = f"""
        return fetch('{url}', {{
            method: 'POST',
            headers: f"{default_headers}",
            body: JSON.stringify({data})
        }}).then(response => {{
            return response.json();
        }}).catch(error => {{
            return {{ error: error.message }};
        }});
        """
        return self.driver.execute_script(script)

    async def execute_get_request(self, url: str, params: Optional[dict] = None) -> Any:
        # Đây là một hàm không đồng bộ, nó dùng trong trường hợp muốn chạy và python không cần dừng chờ kết quả
        default_headers = self.default_headers.copy()
        params_js = f"new URLSearchParams({params}).toString()" if params else "''"

        script = f"""
        const url = new URL('{url}');
        url.search = {params_js};
        const callback = arguments[arguments.length - 1];
        fetch(url.toString(), {{
            method: 'GET',
            headers: f"{default_headers}"
        }}).then(response => response.json())
        .then(data => callback(data))
        .catch(error => callback({{ error: error.message }}));
        """
        return await self.driver.execute_async_script(script)

    async def execute_post_request(self, url: str, data: dict = {}) -> Any:
        # Đây là một hàm không đồng bộ, nó dùng trong trường hợp muốn chạy và python không cần dừng chờ kết quả
        default_headers = self.default_headers.copy()
        default_headers["Content-Type"] = "application/json"

        script = f"""
        const callback = arguments[arguments.length - 1];
        fetch('{url}', {{
            method: 'POST',
            headers: f"{default_headers}",
            body: JSON.stringify({data})
        }}).then(response => response.json())
        .then(data => callback(data))
        .catch(error => callback({{ error: error.message }}));
        """
        return await self.driver.execute_async_script(script)

    def execute_open_game_join_link_ref(self, locator: str, link: str) -> Optional[Any]:
        script = f"""
        (async () => {{
            const refLink = "{link}"; // The link passed from Python

            const urlObj = new URL(refLink);
            const pathnameParts = urlObj.pathname.split("/");
            const nameBot = pathnameParts[1];
            const appname = pathnameParts.length > 2 ? pathnameParts[2] : null;
            const startapp =
                urlObj.searchParams.get("startapp") || urlObj.searchParams.get("start");

            const isJoined = !!document.querySelector(`a[title="@{{nameBot}}"]`);

            if (!isJoined) {{
                // If not joined, create the Telegram Web link and redirect to it
                let encodedParams;
                if (appname) {{
                    encodedParams = encodeURIComponent(
                        `tg://resolve?domain=${{nameBot}}&appname=${{appname}}&startapp=${{startapp}}`
                    );
                }} else {{
                    encodedParams = encodeURIComponent(
                        `tg://resolve?domain=${{nameBot}}&start=${{startapp}}`
                    );
                }}

                const newUrl = `https://web.telegram.org/k/#?tgaddr=${{encodedParams}}`;
                window.location.href = newUrl;
            }} else {{
                const launchButton = document.evaluate(
                "//*[text()='Launch']", // The locator passed from Python
                document,
                null,
                XPathResult.FIRST_ORDERED_NODE_TYPE,
                null
                ).singleNodeValue;

                if (launchButton) {{
                launchButton.click();
                }} else {{
                console.log("Không tìm thấy nút xpath-opengame.");
                }}
            }}
        }})();
        """
        # Execute the script with the provided locator and link
        return self.driver.execute_script(script)

    def execute_js_file(self, js_file_path: str) -> Optional[Any]:
        try:
            with open(js_file_path, "r", encoding='utf-8') as file:
                code_js = file.read()
            return self.driver.execute_script(f"{code_js}")
        except Exception as e:
            print(f"Lỗi khi thực hiện file js với path: {js_file_path}. Error: {e}")
            return None
        
    # def click_element_by_image(self, image_path: str, threshold: float = 0.8, continuous_click: bool = False, click_duration: float = 5.0):
    #     # Chụp ảnh màn hình của trang hiện tại
    #     screenshot = self.driver.get_screenshot_as_png()
    #     screenshot = Image.open(BytesIO(screenshot))
    #     screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    #     # Đọc hình ảnh cần tìm
    #     target_image = cv2.imread(image_path)
    #     target_height, target_width = target_image.shape[:2]

    #     # Chia ảnh chụp màn hình thành 6 phần
    #     height, width, _ = screenshot.shape
    #     sections = [
    #         (0, 0, width // 2, height // 2),  # Phần 1
    #         (width // 2, 0, width, height // 2),  # Phần 2
    #         (0, height // 2, width // 2, height),  # Phần 3
    #         (width // 2, height // 2, width, height),  # Phần 4
    #         (width // 4, height // 4, 3 * width // 4, 3 * height // 4),  # Phần 5 (giữa)
    #         (width // 4, height // 4, 3 * width // 4, 3 * height // 4)  # Phần 6 (giữa)
    #     ]

    #     start_time = time.time()
    #     while True:
    #         found = False
    #         for (x_start, y_start, x_end, y_end) in sections:
    #             # Cắt phần ảnh chụp màn hình
    #             section = screenshot[y_start:y_end, x_start:x_end]

    #             # Tìm kiếm hình ảnh trong phần đã cắt
    #             result = cv2.matchTemplate(section, target_image, cv2.TM_CCOEFF_NORMED)
    #             yloc, xloc = np.where(result >= threshold)

    #             # Nếu tìm thấy hình ảnh
    #             if len(xloc) > 0 and len(yloc) > 0:
    #                 found = True
    #                 for (x, y) in zip(xloc, yloc):
    #                     # Tính toán vị trí click
    #                     click_x = x + x_start + target_width // 2
    #                     click_y = y + y_start + target_height // 2
                        
    #                     # Click vào vị trí tìm thấy
    #                     self.action.move_to_element_with_offset(self.driver.find_element(By.TAG_NAME, 'body'), click_x, click_y).click().perform()
    #                     time.sleep(0.1)  # Thêm một chút thời gian giữa các click

    #         # Nếu không tìm thấy hình ảnh, dừng lại
    #         if not found:
    #             break

    #         # Kiểm tra thời gian click liên tục
    #         if continuous_click and (time.time() - start_time) >= click_duration:
    #             break

    #     if not found:
    #         print("Không tìm thấy hình ảnh trong trang.")
    #     return found