from typing import Literal, Tuple, Optional
import logging
import asyncio
from src.utils import GlobalVariableManager, FileManager
from src.apis import SeleniumAPI, RequestAPI

class AutoMainSync:
    def __init__(self, profile: dict, auto: dict, driver: any, is_export_query_id: bool) -> None:
        self.goto_url = "https://web.telegram.org/k/"
        self.profile = profile
        self.auto = auto
        self.driver = driver
        self.selenium = SeleniumAPI(driver=driver)
        self.is_export_query_id = is_export_query_id
        self.global_variable = GlobalVariableManager()
        self.file_manager = FileManager()
        self.request_api = RequestAPI()
        
    def process_sync_task(self) -> Optional[bool]:
        """Hàm đồng bộ chạy cho từng profile"""
        auto_id = self.auto["id"]
        try:
            return self.handle_switch_case_auto(auto_id)
        except asyncio.CancelledError:
            return
        except Exception as e:
            logging.error(f'Error run auto main sync {e}')
            return False
        
    def open_game(self, xpath_open_game: str, link_ref: str, profile: dict, type_get: Literal["full", "partial", "decode"] = 'partial') -> Tuple[Optional[str], Optional[str]]:
        selenium = self.selenium
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                selenium.close_tab()
                selenium.active_tab(0)
                selenium.open_URL(self.goto_url)
                selenium.execute_open_game_join_link_ref(locator=xpath_open_game, link=link_ref)
                # đợi giao diện tải xong
                selenium.wait_element('//*[@id="folders-container"]/div[1]/div[2]/ul/a[1]', 30)

                if selenium.element_is_exist('//button[@class="popup-button btn primary rp"]/span'):
                    selenium.click_element('//button[@class="popup-button btn primary rp"]')

                query_id = selenium.get_query_id(type_get=type_get)
                proxy = profile["raw_proxy"]
                return query_id, proxy
            except asyncio.CancelledError:
                return
            except Exception as e:
                print(f"Lỗi trong lần thử {attempt + 1}/{max_retries}: {str(e)}")

            print(f"Thử lại lần {attempt + 1}/{max_retries}...")

        print("Không thể lấy được query_id sau 3 lần thử.")
        return None, None
        
    def handle_switch_case_auto(self, auto_id: str) -> Optional[bool]:
        """Xử lý switch case cho auto"""
        # Tạo từ điển ánh xạ các auto_id đến các phương thức tương ứng
        switcher = {
            "auto_blum": self.auto_run_blum,
            "auto_timefarm": self.auto_run_timefarm,
            "auto_create_ton_wallet": self.auto_create_ton_wallet,
            "auto_get_token_magicnewton": self.auto_get_token_magicnewton,
        }
        func = switcher.get(auto_id, None)
        
        return func() if func else False

    def run_auto_task(self, xpath_open_game: str, link_ref: str, type_get: Literal["full", "partial", "decode"] = 'partial') -> bool:
        profile = self.profile
        query_id, proxy = self.open_game(xpath_open_game=xpath_open_game, link_ref=link_ref, profile=profile, type_get=type_get)

        if query_id is None:
            return False

        data = {
            "profile_id": profile["id"],
            "auto_id": self.auto["id"],
            "query_id": query_id,
            "proxy": proxy
        }

        self.global_variable.update_global_data_auto_profiles_temp(data)

        if self.is_export_query_id:
            self.global_variable.append_global_data_query_id_temp(query_id)

        return True
    
    def get_xpath_open_game(self, text: str, type: int = 1) -> str:
        if type == 1:
            return f"(//div[@class='new-message-bot-commands-view' and text()='{text}'])[last()]"
        elif type == 2:
            return f"(//button[*[text()='{text}']])[last()]"
        else:
            raise ValueError("Invalid Xpath open game type")
        
    def auto_run_blum(self):
        xpath_open_game = self.get_xpath_open_game(text="Launch Blum")
        link_ref = "https://t.me/blum/app?startapp=ref_LHzHt1atQz"
        return self.run_auto_task(xpath_open_game=xpath_open_game, link_ref=link_ref)

    def auto_run_timefarm(self):
        selenium = self.selenium
        xpath_open_game = self.get_xpath_open_game(text="Open App", type=2)
        link_ref = "https://t.me/TimeFarmCryptoBot?start=qFUvABmfdvjXjwuE"        
        selenium.close_tab()
        selenium.active_tab(0)
        selenium.open_URL(self.goto_url)
        selenium.execute_open_game_join_link_ref(locator=xpath_open_game, link=link_ref)
        # đợi giao diện tải xong
        selenium.wait_element('//*[@id="folders-container"]/div[1]/div[2]/ul/a[1]', 30)
        selenium.sleep(1.5)
        selenium.click_element(locator=xpath_open_game, delay=2)

        if selenium.element_is_exist('//button[@class="popup-button btn primary rp"]/span'):
            selenium.click_element('//button[@class="popup-button btn primary rp"]')
        query_id = selenium.get_query_id()

        data = {
            "profile_id": self.profile["id"],
            "auto_id": self.auto["id"],
            "query_id": query_id,
            "proxy": self.profile.get('proxy'),
        }

        self.global_variable.update_global_data_auto_profiles_temp(data)

        if self.is_export_query_id:
            self.global_variable.append_global_data_query_id_temp(query_id)
        return True
            
    def auto_create_ton_wallet(self):
        selenium = self.selenium
        id_extension = 'omaabbefbmiijedngplfjmnooppbclkk'
        selenium.open_URL(f'chrome-extension://{id_extension}/index.html?add_wallet=create-standard')
        numeric_code = ''
        password = '/OnS(k(47Q8dL'
        
        if selenium.element_is_exist('//h2[contains(text(), "Grab a pen")]'):
            selenium.click_element("//button[text()='Continue']")
        
        if selenium.element_is_exist('//div[@wordsnumber="24"]'):
            numElement = selenium.get_number_of_elements('//div[@wordsnumber="24"]')
            numeric_code = ""
            list_numeric_code = []
            for i in range(numElement):
                text = selenium.get_text(f'//div[@wordsnumber="24"]/span[{i}]')
                text = text.split('. ')[1]
                numeric_code += f'{text} '
                list_numeric_code.append(text)
            selenium.click_element("//button[text()='Continue']")
            a = selenium.get_text('(//span[@class="sc-jrAGKZ sc-bvVcIm hDTHQe iDCYGN"])[1]')
            a = a.replace(':','')
            a = int(a)
            b = selenium.get_text('(//span[@class="sc-jrAGKZ sc-bvVcIm hDTHQe iDCYGN"])[2]')
            b = b.replace(':','')
            b = int(b)
            c = selenium.get_text('(//span[@class="sc-jrAGKZ sc-bvVcIm hDTHQe iDCYGN"])[3]')
            c = c.replace(':','')
            c = int(c)
            
            selenium.type_text('(//input[@class="sc-fIYMun cibnMt"])[1]', list_numeric_code[a])
            selenium.type_text('(//input[@class="sc-fIYMun cibnMt"])[2]', list_numeric_code[b])
            selenium.type_text('(//input[@class="sc-fIYMun cibnMt"])[3]', list_numeric_code[c])
            selenium.click_element('//button[text()="Continue"]')
            selenium.type_text('(//input[@type="password"])[1]', password)
            selenium.type_text('(//input[@type="password"])[2]', password)
            selenium.click_element('//button[text()="Continue"]')
            selenium.click_element('//button[text()="Save"]')
        selenium.open_URL(f'chrome-extension://{id_extension}/index.html')
        selenium.click_element('//*[@id="body"]/div[2]/div[3]/div')
        address = selenium.get_text('//*[@id="react-portal-modal-container"]/div/div[1]/div/div/div[3]/div/div/form/div[2]/div/div/form/div[2]/span')
        
        data_wallet = f'{self.profile["name"]}|{address}|{numeric_code}|{password}'
        self.file_manager.append_data_to_file(data_wallet, filename='ton_wallet.txt')
        
    def auto_get_token_magicnewton(self):
        selenium = self.selenium
        link_open = "https://www.magicnewton.com/portal/rewards"        
        selenium.close_tab()
        selenium.active_tab(0)
        selenium.open_URL(link_open)
        selenium.sleep(3)
        cookie = selenium.get_cookie('__Secure-next-auth.session-token')
        data = f"{self.profile["name"]}|{cookie['value']}"
        self.file_manager.append_data_to_file(data, filename='cookie_magicnewton.txt')