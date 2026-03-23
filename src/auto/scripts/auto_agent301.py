import time
import datetime
import random
import asyncio
import logging
from src.apis import RequestAPI

class AutoAgent301:
    def __init__(self, query_id: str = None, proxy: str = None):
        self.base_url = 'https://api.agent301.org';
        self.proxy = proxy
        self.query_id = query_id
        logging.info(f"query_id: {query_id}")
        self.token = None
        self.balance_info = None
        self.current_game_id = None
        self.next_time_run = None
        self.custom_headers = {
            'Authorization': query_id,
            'Origin': 'https://telegram.agent301.org',
            'Referer': 'https://telegram.agent301.org/',
        }
        self.request_API = RequestAPI(proxy=proxy, custom_headers=self.custom_headers)
        
    async def process_run_bot(self):
        while True:
            try:
                user_info = await self.getMe()
                if user_info:
                    logging.info(f"Balance: {user_info['result']['balance']}")
                    logging.info(f"Tickets: {user_info['result']['tickets']}")

                    await self.processTasks()
                    await self.handleWheelTasks()

                    if user_info['result']['tickets'] > 0:
                        logging.info("Starting to spin wheel...")
                        await self.spinAllTickets(user_info['result']['tickets'])
                    
                    # Lấy thời gian ngủ cho lần chạy tiếp theo
                    current_timestamp = int(datetime.now().timestamp())
                    next_time, date_time = self.request_API.get_sleep_until(current_timestamp+3600)
                    logging.info(f"Chờ đến lần chạy tiếp theo sau: {date_time}.")
                    await asyncio.sleep(next_time) 
                else:
                    raise Exception('Không thể lấy thông tin user')
            except Exception as e:
                logging.error(f"Lỗi khi chạy process_run_bot Auto 301: {str(e)}", exc_info=True)
                await asyncio.sleep(5)  
                
    async def processTasks(self):
        try:
            tasks = await self.getTasks()
            unclaimed_tasks = [task for task in tasks if not task.get('is_claimed') and task['type'] not in ['nomis2', 'boost', 'invite_3_friends']]
            
            if not unclaimed_tasks:
                logging.error("No unclaimed tasks remaining.")
                return

            for task in unclaimed_tasks:
                remaining_count = task.get('max_count', 1) - task.get('count', 0)
                for i in range(remaining_count):
                    await self.completeTask(task['type'], task['title'], i, remaining_count)
                    await asyncio.sleep(1)
        except Exception as e:
            logging.error(f"Error processing tasks: {str(e)}")
            
    async def handleWheelTasks(self):
        try:
            wheel_data = await self.wheelLoad()
            current_timestamp = int(time.time())

            # Handle daily task
            if current_timestamp > wheel_data['tasks']['daily']:
                daily_result = self.wheel_task('daily')
                next_daily = datetime.fromtimestamp(daily_result['tasks']['daily']).isoformat()
                logging.info(f"Claim daily ticket thành công. Lần claim tiếp theo: {next_daily}")
                wheel_data = daily_result
            else:
                next_daily = datetime.fromtimestamp(wheel_data['tasks']['daily']).isoformat()
                logging.info(f"Thời gian claim daily ticket tiếp theo: {next_daily}", 'info')

            # Handle bird task
            if not wheel_data['tasks'].get('bird'):
                bird_result = self.wheel_task('bird')
                logging.info('Làm nhiệm vụ ticket bird thành công')
                wheel_data = bird_result

            # Handle hourly task
            hour_count = wheel_data['tasks']['hour']['count']
            while hour_count < 5 and current_timestamp > wheel_data['tasks']['hour']['timestamp']:
                hour_result = self.wheel_task('hour')
                hour_count = hour_result['tasks']['hour']['count']
                logging.info(f"Làm nhiệm vụ hour thành công. Lần thứ {hour_count}/5")
                wheel_data = hour_result

            if hour_count == 0 and current_timestamp < wheel_data['tasks']['hour']['timestamp']:
                next_hour = datetime.fromtimestamp(wheel_data['tasks']['hour']['timestamp']).isoformat()
                logging.info(f"Thời gian xem video claim ticket tiếp theo: {next_hour}")

            return wheel_data
        except Exception as e:
            logging.error(f"Error handling wheel tasks: {str(e)}")
        
    async def getMe(self):
        url = f"{self.base_url}/getMe"
        data = {"referrer_id": 376905749}
        
        try:
            response = await self.request_API.execute_post_request(url, data)
            if response:
                return response
            return None
        except Exception as e:
            logging.error(f"Failed to get user info: {str(e)}")

    async def completeTask(self, taskType, taskTitle, currentCount=0, maxCount=1):
        url = f"{self.base_url}/completeTask"
        data = {"type": taskType}
        
        try:
            response = await self.request_API.execute_post_request(url, data)
            result = response.get('result')
            logging.info(f"Completed task {taskTitle} {currentCount + 1}/{maxCount} successfully | Reward {result['reward']} | Balance {result['balance']}")
            return result
        except Exception as e:
            logging.error(f"Failed to complete task {taskTitle}: {str(e)}")

    async def getTasks(self):
        url = f"{self.base_url}/getTasks"
        data = {}
        
        try:
            response = await self.request_API.execute_post_request(url, data)
            return response.get('result').get('data')
        except Exception as e:
            logging.error(f"Error fetching task list: {str(e)}")

    async def spinWheel(self):
        url = f"{self.base_url}/wheel/spin"
        data = {}
        
        try:
            response = await self.request_API.execute_post_request(url, data)
            result = response['result']
            logging.info(f"Successfully spun the wheel: Received {result['reward']}")
            logging.info(f"* Balance : {result.balance}");
            logging.info(f"* Toncoin : {result.toncoin}");
            logging.info(f"* Notcoin : {result.notcoin}");
            logging.info(f"* Tickets : {result.tickets}");
            return result
        except Exception as e:
            logging.error(f"Failed to spin the wheel: {str(e)}")

    async def spinAllTickets(self, initial_tickets):
        tickets = initial_tickets
        while tickets > 0:
            try:
                result = await self.spinWheel()
                tickets = result['tickets']
            except Exception as e:
                logging.error(f"Error spinning tickets: {str(e)}")
                break
            await asyncio.sleep(1)
        logging.error("Used up all tickets.")

    async def wheelLoad(self):
        url = f"{self.base_url}/wheel/load"
        data = {}
        
        try:
            response = await self.request_API.execute_post_request(url, data)
            return response['result']
        except Exception as e:
            logging.error(f"Error loading wheel: {str(e)}")

    async def wheelTask(self, task_type):
        url = f"{self.base_url}/wheel/task"
        data = {"type": task_type}
        
        try:
            response = await self.request_API.execute_post_request(url, data)
            return response['result']
        except Exception as e:
            logging.error(f"Error performing wheel task {task_type}: {str(e)}")

   