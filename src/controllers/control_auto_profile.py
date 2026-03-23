import asyncio
import logging
from qasync import asyncSlot
from PySide6.QtWidgets import QMessageBox, QCheckBox
from src.apis import  GPMLoginAPI
from src.utils import GlobalVariableManager, FileManager, BrowserManager
from src.auto import AutoMainSync, AutoMainAsync
from src.auto.scripts import AutoAgent301

class ControlAutoProfile:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.profiles_selected = []
        self.auto_selected = []
        self.profile_states = {}
        self.global_variable = GlobalVariableManager()
        self.browser_manager = BrowserManager()
        self.gpm_api = GPMLoginAPI()
        self.semaphore = None
        self.is_export_query_id = None
        self.is_hidden_browser = None

        self.main_window.btn_run_auto.clicked.connect(self.handle_click_run_auto)
        self.main_window.btn_stop_auto.clicked.connect(self.handle_click_stop_auto)
        
        self.window_configurations = []
        self.async_retry_list = []  # Danh sách lưu các profile và auto gặp lỗi async
        self.running_tasks_sync = []  # Danh sách lưu các task đang chạy theo [auto_id, profile_id, task]
        self.running_tasks_async = []  # Danh sách lưu các task đang chạy theo [auto_id, profile_id, task]
    
    @asyncSlot() 
    async def handle_click_run_auto(self):
        """Bắt đầu quá trình chạy auto khi nhấn nút 'Run Auto'"""
        max_workers = int(self.main_window.in_max_threads.text()) if self.main_window.in_max_threads.text() else 5
        self.semaphore = asyncio.Semaphore(max_workers)
        self.is_export_query_id = self.main_window.cb_export_query_id.isChecked()
        self.is_hidden_browser = self.main_window.cb_hidden_browser.isChecked()
        self.profiles_selected = self.global_variable.get_global_profiles_selected().copy()
        self.auto_selected = self.global_variable.get_global_auto_selected().copy()
        self.handle_ui(False)
        self.main_window.btn_stop_auto.setEnabled(True)

        window_config = self.browser_manager.calculate_window_layout(profiles_selected=self.profiles_selected, max_workers=max_workers)
        self.window_configurations = {config['id']: config for config in window_config}
       
        try:
            await self.run_all_autos()
        except Exception as e:
            logging.error(f"Error occurred while running autos: {e}", exc_info=True)
            QMessageBox(None, "Error", f"Error occurred: {e}")
        finally:
            self.handle_ui(True)
    
    @asyncSlot() 
    def handle_click_stop_auto(self, close_all:bool = False):
        async def stop_auto():   
            """Dừng quá trình chạy auto khi nhấn nút 'Stop Auto'"""
            tasks_sync_to_cancel = []
            tasks_async_to_cancel = []
            
            try:
                if self.running_tasks_sync:
                    # Hủy tất cả task sync
                    for task in self.running_tasks_sync:
                        task.cancel()
                        tasks_sync_to_cancel.append(task)

                    await asyncio.gather(*tasks_sync_to_cancel, return_exceptions=True)
                    self.running_tasks_sync.clear()

                if self.running_tasks_async:
                    if close_all:
                        # Hủy tất cả task async
                        for auto, profile, task in self.running_tasks_async:
                            task.cancel()
                            tasks_async_to_cancel.append(task)

                    else:
                        # Hủy task cụ thể theo auto_ids và profile_ids
                        auto_ids = {auto['id'] for auto in self.auto_selected} if self.auto_selected else {None}
                        profile_ids = {profile['id'] for profile in self.profiles_selected} if self.profiles_selected else {None}

                        for auto, profile, task in self.running_tasks_async:
                            if (auto in auto_ids or None in auto_ids) and (profile in profile_ids or None in profile_ids):
                                task.cancel()
                                tasks_async_to_cancel.append(task)

                    await asyncio.gather(*tasks_async_to_cancel, return_exceptions=True)
                    self.running_tasks_async = [t for t in self.running_tasks_async if t[2] not in tasks_async_to_cancel]
                await asyncio.sleep(0)

            finally:
                if not self.running_tasks_async:
                    self.handle_ui(True)

                logging.info("Stopped auto tasks successfully.")
        
        return asyncio.ensure_future(stop_auto())

    async def run_all_autos(self):
        """Chạy tuần tự tất cả các auto với danh sách profile đã chọn"""
        # await Auto301().process_run_bot()
        try:
            for auto in self.auto_selected:
                if not auto.get('ready_run', False):
                    logging.info(f"{auto['auto_name']} is maintaining, please try again later.")
                    continue
                await self.run_profiles_for_auto(auto)

            if self.async_retry_list:
                await self.retry_failed_profiles()

            await self.monitor_async_errors()

        except Exception as e:
            logging.error(f"Error while running autos: {e}", exc_info=True)

    async def run_profiles_for_auto(self, auto: any):
        """Chạy danh sách các profile với auto hiện tại"""
        auto_id = auto.get("id")
        ready_run = auto.get("ready_run", False)
        run_async = auto.get("run_async", False)
        
        if not ready_run:
            logging.info(f"Auto {auto_id} is not ready to run.")
            return
        
        # Chạy các task sync với giới hạn
        sync_tasks = [
            asyncio.create_task(self.run_task_with_limit(lambda profile=profile, auto=auto: self.run_sync_tasks(profile=profile, auto=auto)))
            for profile in self.profiles_selected
        ]
        
        # Thêm task vào danh sách để quản lý và có thể hủy chúng khi cần
        self.running_tasks_sync.extend(sync_tasks)
        
        # Chờ cho tất cả các task sync hoàn tất
        sync_results = await asyncio.gather(*sync_tasks)
        
        # Xoá các task đã hoàn thành khỏi danh sách
        self.running_tasks_sync.clear()
        
        for result, profile in zip(sync_results, self.profiles_selected):
            profile_id = profile.get("id")
            profile_name = profile.get("name")
            if isinstance(result, asyncio.CancelledError):
                logging.warning(f"Task for profile {profile_name} in auto - {auto_id} was cancelled.")
                
            if isinstance(result, Exception):
                logging.error(f"Skipping task for profile {profile_name} in auto - {auto_id} due to failed sync task: {result}")
                continue
          
            if run_async:
                await self.manage_async_task(auto, profile)
                
        # Append data vào file khi task sync thành công
        FileManager().append_data_to_file_data()
        if self.is_export_query_id:
            FileManager().append_data_query_id_to_file(filename=auto_id)

    async def run_sync_tasks(self, profile: any, auto: any):
        """Chạy các hàm đồng bộ cho một profile với auto, sử dụng ThreadPoolExecutor."""
        profile_id = profile.get("id")
        profile_name = profile.get("name")
        auto_id = auto.get("id")
        logging.info(f"Running sync task for profile {profile_name} in auto - {auto_id}")
        window_config = self.window_configurations.get(profile_id)

        driver = self.gpm_api.start(profileId=profile_id, isOneProfile=len(self.profiles_selected) == 1, runHideUi=self.is_hidden_browser, winPos=window_config.get('winPos'), winScale=window_config.get('winScale'), winSize=window_config.get('winSize'))
        if not driver:
            return False

        def sync_task():
            """Nhiệm vụ xử lý đồng bộ."""
            task = AutoMainSync(profile=profile, auto=auto, driver=driver, is_export_query_id=self.is_export_query_id)
            
            try:
                return task.process_sync_task()
            except asyncio.CancelledError:
                return
            except Exception as e:
                logging.error(f"Error sync task for profile {profile_name}: {e}")
                return False
            
        try:
            result = await asyncio.get_event_loop().run_in_executor(None, sync_task)
            await asyncio.sleep(0)
            return result
        except asyncio.CancelledError:
            return
        finally:
            self.gpm_api.stop(profile_id)

    async def handle_async_with_retry(self, profile: any, auto: any):
        """Xử lý retry cho hàm bất đồng bộ"""
        profile_id = profile.get("id")
        profile_name = profile.get("name")
        auto_id = auto.get("id")

        try:
            logging.info(f"Running async task for profile {profile_name} in auto - {auto_id}")
            data_auto_profile = FileManager().get_data_from_file_data_by_profile_and_auto_id(profile_id, auto_id)
            await AutoMainAsync(profile=profile, auto=auto, data_auto_profile=data_auto_profile).process_async_task()
            await asyncio.sleep(0)
        except asyncio.CancelledError:
            logging.info(f"Async task for profile {profile_name} in auto - {auto_id} was canceled.")
            return  # Kết thúc ngay lập tức sau khi bị hủy
        except Exception as e:
            logging.error(f"Async task error for profile {profile_name} in auto - {auto_id}. Error: {e}", exc_info=True)
            self.async_retry_list.append((profile, auto))
    
    async def retry_failed_profiles(self):
        tasks_retry = [
            asyncio.create_task(self.run_task_with_limit(lambda profile=profile, auto=auto: self.retry_single_profile(profile, auto)))
            for profile, auto in self.async_retry_list
        ]
        await asyncio.gather(*tasks_retry, return_exceptions=True)
        self.async_retry_list.clear()

    async def monitor_async_errors(self):
        """Theo dõi các task async để phát hiện và xử lý lỗi"""
        try:
            while self.running_tasks_async:
                done, _ = await asyncio.wait(
                    [task for a, p, task in self.running_tasks_async],
                    return_when=asyncio.FIRST_EXCEPTION
                )

                retry_tasks = []

                # Xử lý các task đã hoàn thành
                for task in done:
                    if task.exception():
                        auto_id, profile_id = next(((a, p) for a, p, t in self.running_tasks_async if t == task), (None, None))
                        if auto_id and profile_id:
                            # Lấy dữ liệu profile và auto tương ứng
                            profile = next(p for p in self.global_variable.get_global_list_data_profiles() if p["id"] == profile_id)
                            auto = next(a for a in self.global_variable.get_global_list_data_auto() if a["id"] == auto_id)   
                            retry_tasks.append(asyncio.create_task(self.run_task_with_limit(lambda profile=profile, auto=auto: self.retry_single_profile(profile, auto))))

                if retry_tasks:
                    await asyncio.gather(*retry_tasks, return_exceptions=True)
                    await asyncio.sleep(0)
                    retry_tasks.clear()

                await asyncio.sleep(33)
        finally:
            self.main_window.btn_stop_auto.setEnabled(False)

    async def run_task_with_limit(self, process):
        async with self.semaphore:
            try:
                result = process()
                await asyncio.sleep(0)
                if asyncio.iscoroutine(result):
                    return await result
                else:
                    return result
                
            except asyncio.CancelledError:
                return
            except Exception as e:
                logging.error(f"Task failed with exception: {e}")
                raise
            finally:
                ...
  
    async def manage_async_task(self, auto: any, profile: any):
        """Quản lý các task async và đảm bảo không có task nào bị chạy trùng lặp"""
        auto_id = auto.get("id")
        profile_id = profile.get("id")
        profile_name = profile.get("name")

        # Kiểm tra xem task async nào cho profile_id và auto_id đã chạy hay chưa
        existing_task = next((task for a, p, task in self.running_tasks_async if a == auto_id and p == profile_id), None)

        # Nếu đã có task đang chạy thì hủy nó
        if existing_task:
            logging.info(f"Canceling running task for profile {profile_name} in auto - {auto_id}")
            existing_task.cancel()

        # Tạo task mới cho profile
        new_task = asyncio.create_task(self.handle_async_with_retry(profile, auto))

        # Cập nhật danh sách task
        self.running_tasks_async = [t for t in self.running_tasks_async if not (t[0] == auto_id and t[1] == profile_id)]
        self.running_tasks_async.append((auto_id, profile_id, new_task))

        await asyncio.gather(new_task, return_exceptions=True)
        await asyncio.sleep(0)
        
        
    async def retry_single_profile(self, profile: any, auto: any):
        """Hàm retry cho từng profile"""
        profile_name = profile.get("name")
        auto_id = auto.get("id")
        logging.info(f"Retrying failed profile {profile_name} in auto - {auto_id}")
        
        # Chạy lại task sync trước khi chạy task async
        sync_success = await self.run_sync_tasks(profile, auto)
        await asyncio.sleep(0)

        if sync_success:
            FileManager().append_data_to_file_data()
            if self.is_export_query_id:
                FileManager().append_data_query_id_to_file(filename=auto['id'], is_append=True)
            task = asyncio.create_task(self.handle_async_with_retry(profile, auto))
            self.running_tasks_async.append((auto['id'], profile['id'], task))
            await asyncio.gather(task, return_exceptions=True)
            
    def handle_ui(self, state: bool):
        # Disable buttons and tables
        self.main_window.in_max_threads.setEnabled(state)
        self.main_window.cb_export_query_id.setEnabled(state)
        self.main_window.btn_reload_profiles.setEnabled(state)
        self.main_window.btn_run_auto.setEnabled(state)
        self.main_window.btn_select_all_profiles.setEnabled(state)
        self.main_window.btn_select_all_auto.setEnabled(state)
        
        # Disable checkbox
        for row in range(self.main_window.table_list_profiles.rowCount()):
            widget = self.main_window.table_list_profiles.cellWidget(row, 0)
            if widget:
                checkbox = widget.findChild(QCheckBox)
                checkbox.setEnabled(state)
                
        for row in range(self.main_window.table_list_auto.rowCount()):
            widget = self.main_window.table_list_auto.cellWidget(row, 0)
            if widget:
                checkbox = widget.findChild(QCheckBox)
                checkbox.setEnabled(state)