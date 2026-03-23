import atexit
import os
import psutil
import asyncio
import logging
from sys import platform
from PySide6.QtCore import QTimer

from src.utils import GlobalVariableManager, FileManager

"""Control Common module"""
class ControlCommon:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance
    
    def __init__(self, main_window: any, control_auto_profile: any) -> None:
        self.main_window = main_window
        self.control_auto_profile = control_auto_profile
        self.load_config_data()

        atexit.register(self.save_config_on_exit)
        atexit.register(self.close_all_thread)

    def load_config_data(self) -> None:
        config_data = FileManager().load_data_from_config_folder()

        if config_data:
            GlobalVariableManager().update_global_config_common(config_data)
            value_global_config_common = GlobalVariableManager().get_global_config_common()

            if 'profiles_path' in value_global_config_common:
                pass
                # self.main_window.in_profiles_path.setText(value_global_config_common['profiles_path'])

    def save_config_on_exit(self) -> None:
        data_config = GlobalVariableManager().get_global_config_common()
        if not data_config:
            data_config = {
                'profiles_path': '',
            }
        # FileManager().save_data_to_config_folder(data_config)

    def close_all_thread(self) -> None:
        async def close_all_thread_async() -> None:
            try:
                print('Closing all thread...')
                await self.control_auto_profile.handle_click_stop_auto(close_all=True)
                if platform == "win32":
                    for proc in psutil.process_iter():
                        if "chromedriver" in proc.name():
                            proc.kill()
                else:
                    os.system('killall -9 chromedriver')
                print('Closed all thread.')
            except Exception as e:
                logging.error(f'Error when close all thread: {e}', exc_info=True)  
        
        def close() -> None:
            asyncio.run(close_all_thread_async())
            
        QTimer.singleShot(0, close)
