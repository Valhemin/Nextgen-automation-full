import requests
import asyncio
from typing import TypedDict, Union, Literal, NotRequired
from .undetect_chrome_driver_api import UndetectChromeDriver
from seleniumbase import BaseCase

class ResOpenProfileData(TypedDict):
    driver: UndetectChromeDriver
   
class ResponseGetProfilesData(TypedDict):
    id: str
    name: str
    raw_proxy: str
    browser_type: str
    browser_version: str
    group_id: str
    profile_path: str
    note: str
    created_at: str

class ResponseGetGroupsData(TypedDict):
    id: int
    name: str
    sort: int
    created_by: int
    created_at: str
    updated_at: str

class NewProfileData(TypedDict):
    profile_name: str
    group_id: NotRequired[int]
    raw_proxy: NotRequired[str]
    startup_urls: NotRequired[str]
    note: NotRequired[str]
    color: NotRequired[str]
    user_agent: NotRequired[Union[Literal['auto'], str]]


class GPMLoginAPI(BaseCase):
    API_START_PATH = "/api/v3/profiles/start"
    API_STOP_PATH = "/api/v3/profiles/close"
    API_GET_PROFILES = "/api/v3/profiles"
    API_GET_GROUPS = "/api/v3/groups"
    API_UPDATE_PROFILE = "/api/v3/profiles/update"
    
    def __init__(self, apiUrl: str = 'http://127.0.0.1:19995'):
        super().__init__()
        self._apiUrl = apiUrl

    def start(self, profileId: str, isOneProfile: bool = False, runHideUi: bool = False, addinationArgs: str = '', winScale: float = 0.8, winPos: str = '0,0', winSize: str = '400,500') -> ResOpenProfileData:
        try:
            if(isOneProfile):
                url = f"{self._apiUrl}{self.API_START_PATH}/{profileId}?win_scale=1&win_pos={winPos}&win_size=1200,1200"
            else:
                url = f"{self._apiUrl}{self.API_START_PATH}/{profileId}?win_scale={winScale}&win_pos={winPos}&win_size={winSize}"
           
            if addinationArgs != '':
                url += f"&addination_args={addinationArgs}"
            
            resp = requests.get(url).json()
            if(resp != None):
                status = bool(resp['success'])
                if(status):
                    resp = resp['data']
                    self.driver = UndetectChromeDriver(driverPath=resp["driver_path"], remoteDebugAddress=resp["remote_debugging_address"], runHideUi=runHideUi)
                    self.driver.GetByGpm("https://www.google.com/")
                    return self.driver
                else:
                    raise Exception(f'Profile with id - {profileId}, Error - {resp["message"]}')
        except Exception as e:
            print(f"Error gpm api start: {str(e)}")
            return None
            
        except asyncio.CancelledError:
            return None
    
    def stop(self, profileId: str):
        url = f"{self._apiUrl}{self.API_STOP_PATH}/{profileId}"
        requests.get(url)
        self.driver.quit()

    def get_profiles(self, groupId: int = 1, sort: Literal[0,1,2,3] = 2, newApiUrl: str = None) -> ResponseGetProfilesData:
        try:
            if newApiUrl:
                self._apiUrl = newApiUrl
            url = f"{self._apiUrl}{self.API_GET_PROFILES}?group_id={groupId}&sort={sort}&per_page=100000"
            resp = requests.get(url).json()
            if(resp != None):
                success = bool(resp['success'])
                if(success):
                    return resp['data']
            return []
        except Exception as e:
            print(f"Lỗi khi lấy profiles: {e}")
            return []
    
    def get_groups(self) -> ResponseGetGroupsData:
        try:
            url = f"{self._apiUrl}{self.API_GET_GROUPS}"
            resp = requests.get(url).json()
            if(resp != None):
                success = bool(resp['success'])
                if(success):
                    return resp['data']
            return []
        except Exception as e:
            print(f"Lỗi khi lấy groups: {e}")
            return []

    def update_profile(self, profileId: str, newData: NewProfileData):
        try:
            url = f"{self._apiUrl}{self.API_UPDATE_PROFILE}/{profileId}"
            requests.post(url, json=newData)
        except Exception as e:
            print(f"Lỗi khi update profile {profileId}: {e}")
            return None