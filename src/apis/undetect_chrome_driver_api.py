import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service as ChromeService
from seleniumwire import webdriver
import logging

class UndetectChromeDriver(webdriver.Chrome):
    def __init__(self, driverPath: str, remoteDebugAddress: str, runHideUi: bool, platformType="win"):
        options = uc.ChromeOptions()
        options.debugger_address = remoteDebugAddress
        options.add_argument('--turn-off-whats-new')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-infobars')
        options.add_argument('--no-sandbox')
        options.add_argument('--mute-audio')
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-dev-shm-usage")
        if runHideUi:
            options.add_argument('--headless=new')
        
        # Tùy chỉnh user-agent và navigator dựa trên platformType
        if platformType == "android":
            options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 10; Mobile; rv:89.0) Gecko/89.0 Firefox/89.0')
        elif platformType == "ios":
            options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A5370a Safari/604.1')
        elif platformType == "mac":
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36')
       
        self.platformType = platformType
        super().__init__(service=ChromeService(driverPath), options=options)
        self.removeCdcProps()
        
    def hasCdcProps(self):
        return self.execute_script(
            """
            let objectToInspect = window,
                result = [];
            while(objectToInspect !== null) 
            { result = result.concat(Object.getOwnPropertyNames(objectToInspect));
              objectToInspect = Object.getPrototypeOf(objectToInspect); }
            return result.filter(i => i.match(/.+_.+_(Array|Promise|Symbol)/ig))
            """
        )

    def removeCdcProps(self):
        try:
            if self.platformType == "android":
                platformScript = """
                    Object.defineProperty(navigator, 'platform', { get: () => 'Android' });
                    Object.defineProperty(navigator, 'userAgent', { get: () => 'Mozilla/5.0 (Linux; Android 10; Mobile; rv:89.0) Gecko/89.0 Firefox/89.0' });
                    Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });  // Giả lập 4GB RAM
                """
            elif self.platformType == "ios":
                platformScript = """
                    Object.defineProperty(navigator, 'platform', { get: () => 'iPhone' });
                    Object.defineProperty(navigator, 'userAgent', { get: () => 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A5370a Safari/604.1' });
                """
            elif self.platformType == "mac":
                platformScript = """
                    Object.defineProperty(navigator, 'platform', { get: () => 'MacIntel' });
                    Object.defineProperty(navigator, 'userAgent', { get: () => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36' });
                """
            else:
                # Mặc định là Windows
                platformScript = """
                    Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
                """
            platformScript = ""
                
            # Thêm vào các thuộc tính khác của navigator
            self.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {
                    "source": f"""
                        Object.defineProperty(navigator, 'webdriver', {{ get: () => undefined }});
                        Object.defineProperty(navigator, 'languages', {{ get: () => ['en-US', 'en'] }});
                        Object.defineProperty(navigator, 'plugins', {{ get: () => [112312312312, 212783978123, 3317239712, 4123123123, 5123123123] }});
                        Object.defineProperty(navigator, 'mimeTypes', {{get: function() {{ return {{"0":{{}}, "1":{{}}, "2":{{}}, "3":{{}} }}; }}}});
                        {platformScript}
                        Object.defineProperty(window, 'screenX', {{ get: () => 1640 }}); 
                        Object.defineProperty(window, 'screenY', {{ get: () => 900 }}); 
                        Object.defineProperty(window, 'outerWidth', {{ get: () => 1640 }}); 
                        Object.defineProperty(window, 'outerHeight', {{ get: () => 900 }}); 
                    """
                }
            )
        except Exception as e:
            logging.error(f"Error removing CDC properties: {e}", exc_info=True)

        if self.hasCdcProps():
            self.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {
                    "source": """
                        let objectToInspect = window,
                            result = [];
                        while(objectToInspect !== null) 
                        { result = result.concat(Object.getOwnPropertyNames(objectToInspect));
                        objectToInspect = Object.getPrototypeOf(objectToInspect); }
                        result.forEach(p => p.match(/.+_.+_(Array|Promise|Symbol)/ig)
                                            &&delete window[p]&&console.log('removed',p))
                    """
                },
            )
            
    def GetByGpm(self, url: str):
        super().get(url)  