import asyncio
import logging
from src.auto.scripts import AutoBlum

class AutoMainAsync:
    def __init__(self, profile: dict, auto: dict, data_auto_profile: dict) -> None:
        self.profile = profile
        self.auto = auto
        self.data_auto_profile = data_auto_profile

    async def process_async_task(self) -> None:
        """Hàm bất đồng bộ chạy cho từng profile"""
        try:
            await self.handle_switch_case_auto(self.auto["id"])
        except asyncio.CancelledError:
            return
        except Exception as e:
            raise e

    async def handle_switch_case_auto(self, auto_id: str) -> None:
        query_id = self.data_auto_profile.get("query_id")
        proxy = self.data_auto_profile.get("proxy")
        
        switch_case = {
            "auto_blum": lambda: AutoBlum(query_id=query_id, proxy=proxy).process_run_bot(),
        }
        
        # Lấy hàm tương ứng từ từ điển và gọi nó
        action = switch_case.get(auto_id)
        
        if action:
            await action()
            