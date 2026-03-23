import requests
import aiohttp
import math
import time
import json
import logging
from typing import Optional, Dict, Any
from .headers import headers

class RequestAPI:
    def __init__(self, proxy: Optional[str] = None, custom_headers: Optional[Dict[str, str]] = None, custom_user_agent: Optional[str] = None):
        self.default_headers = headers.copy()
        self.proxy = None
        if custom_headers:
            self.default_headers.update(custom_headers)
        
        if custom_user_agent:
            self.update_user_agent(custom_user_agent)
        
        if proxy:
            self.proxy = self.check_proxy(proxy)

    def update_user_agent(self, user_agent: str) -> None:
        self.default_headers['User-Agent'] = user_agent
        platform_mapping = {
            'Android': ('?1', '"Android"'),
            'iPhone': ('?1', '"iOS"'),
            'Windows': ('?0', '"Windows"'),
            'Macintosh': ('?0', '"macOS"')
        }
        for key, (mobile, platform) in platform_mapping.items():
            if key in user_agent:
                self.default_headers.update({
                    'sec-ch-ua-mobile': mobile,
                    'sec-ch-ua-platform': platform
                })
                break

    @staticmethod
    def get_sleep_until(timestamp_ms: int, use_24_hour: bool = False) -> tuple[int, str]:
        current_time_ms = int(time.time() * 1000)
        remaining_time_ms = timestamp_ms - current_time_ms
        if remaining_time_ms > 0:
            remaining_time_s = math.ceil(remaining_time_ms / 1000)
            time_format = '%d-%m-%Y %H:%M' if use_24_hour else '%d-%m-%Y %I:%M %p'
            return remaining_time_s, time.strftime(time_format, time.localtime(timestamp_ms / 1000))
        return 2000, ''

    def convert_proxy(self, proxy: str) -> str:
        if not proxy.startswith(("http://", "https://")):
            return ''
        
        proxy = proxy.replace("http://", "").replace("https://", "")
        parts = proxy.split(':')
        
        if len(parts) == 4:
            ip, port, username, password = parts
            return f'http://{username}:{password}@{ip}:{port}'
        elif len(parts) == 2:
            ip, port = parts
            return f'http://{ip}:{port}'
        
        raise ValueError("Invalid proxy format. Must be 'ip:port' or 'ip:port:username:password'.")

    async def check_proxy(self, proxy: str, timeout: int = 5) -> Optional[Dict[str, str]]:
        if not proxy or proxy in ['', 'Local']:
            raise ValueError("Invalid proxy")
        
        converted_proxy = self.convert_proxy(proxy)
        if not converted_proxy:
            return None

        test_url = 'https://www.python.org/'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(test_url, proxy=converted_proxy, timeout=timeout) as rp:
                    if rp.status == 200:
                        return converted_proxy
        except aiohttp.ClientError:
            pass
        return None

    def update_headers(self, headers: Dict[str, str]) -> None:
        self.default_headers.update(headers)

    def get_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            proxies = None
            if self.proxy:
                proxies = {
                    'http': self.proxy,
                    'https': self.proxy
                }
            response = requests.get(url, params=params, headers=self.default_headers, proxies=proxies)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.warning(f"GET request failed for URL {url}: {str(e)}")
            return None

    def post_request(self, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        proxies = None
        if self.proxy:
            proxies = {
                'http': self.proxy,
                'https': self.proxy
            }
        headers = self.default_headers.copy()
        headers['Content-Type'] = 'application/json'
        
        try:
            json_data = json.dumps(data) if data and not isinstance(data, str) else data
            response = requests.post(url, data=json_data, headers=headers, proxies=proxies)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.warning(f"POST request failed for URL {url}: {str(e)}")
            return None

    async def execute_get_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        async with aiohttp.ClientSession(headers=self.default_headers) as session:
            try:
                async with session.get(url, params=params, proxy=self.proxy) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                logging.warning(f"Async GET request failed for URL {url}: {str(e)}")
                return None

    async def execute_post_request(self, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        headers = self.default_headers.copy()
        headers['Content-Type'] = 'application/json'
        
        async with aiohttp.ClientSession(headers=headers) as session:
            try:
                async with session.post(url, json=data, proxy=self.proxy) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                logging.warning(f"Async POST request failed for URL {url}: {str(e)}")
                return None