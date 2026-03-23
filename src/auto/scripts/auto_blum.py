import time
import random
import asyncio
import logging
from src.apis import RequestAPI

class AutoBlum:
    def __init__(self, query_id: str, proxy: str | None = None) -> None:
        self.query_id = query_id
        if not self.query_id:
            raise ValueError('Auto Blum query_id trống')
        self.token = None
        self.balance_info = None
        self.current_game_id = None
        self.next_time_run = None
        self.custom_headers = {
            "Origin": 'https://telegram.blum.codes',
            "Referer": 'https://telegram.blum.codes/',
        }
        self.request_API = RequestAPI(proxy=proxy, custom_headers=self.custom_headers)
        self.task_keywords = None
        
    async def process_run_bot(self):
        try:
            while True:
                if await self.getNewToken():
                    if await self.getUserInfo():
                        await self.process_run_claim()
                        await self.process_do_tasks()
                        await self.process_run_game()
                        # Lấy thời gian ngủ cho lần chạy tiếp theo
                        next_time, date_time = self.request_API.get_sleep_until(self.next_time_run)
                        logging.info(f"Chờ đến lần chạy tiếp theo sau: {date_time}.")
                        await asyncio.sleep(next_time)  # Chờ đến thời gian tiếp theo
                    else: 
                        raise Exception('Lỗi lấy thông tin người dùng')
                else:
                    raise Exception('Không thể lấy token mới')
                
        except Exception as e:
            # Chờ vài giây trước khi thử lại nếu có lỗi
            await asyncio.sleep(5)
            raise e
            
    async def process_run_claim(self):
        if await self.checkDailyReward():
            logging.info('Đã nhận daily reward thành công!')
        self.balance_info = await self.getBalance()
        if self.balance_info:
            if self.balance_info.get('farming'):
                self.next_time_run = int(self.balance_info.get('farming').get("endTime"))
                current_time = int(time.time() * 1000)
                if current_time > self.next_time_run:
                    farming_result = await self.claimBalance()
                    if farming_result:
                        logging.info('Đã nhận farming thành công!')
                    farming_result = await self.startFarming()
                    if farming_result:
                        logging.info('Đã bắt đầu farming thành công!')
            else:
                farming_result = await self.startFarming()
                if farming_result:
                    logging.info('Đã bắt đầu farming thành công!')
        friend_balance_info = await self.checkBalanceFriend()
        if friend_balance_info.get('amountForClaim') and float(friend_balance_info.get('amountForClaim')) > 0:
            claim_friend_balance_result = await self.claimBalanceFriend()
            if claim_friend_balance_result:
                logging.info('Đã nhận số dư bạn bè thành công!')
                    
        try:
            status_tribe = await self.getStatusTribe()
        except Exception as e:    
            try:
                join_tribes_result = await self.joinTribes('0999c4b7-1bbd-4825-a7a0-afc1bfb3fff6')
                if join_tribes_result:
                    logging.info('Đã tham gia tribes thành công!')
            except Exception as e:
                logging.warning(f'Không thể tham gia tribes: {e}')
    
    async def process_do_tasks(self):
        task_list_response = await self.getTasks()
        if task_list_response:
            all_tasks = [task for section in task_list_response for task in (section.get('tasks') or [])]
            
            # Thêm phần xử lý sub tasks
            for section in task_list_response:
                sub_sections = section.get('subSections')
                if sub_sections and isinstance(sub_sections, list):
                    for sub_section in sub_sections:
                        sub_section_tasks = sub_section.get('tasks')
                        if sub_section_tasks and isinstance(sub_section_tasks, list):
                            all_tasks.extend(sub_section_tasks)
            
            logging.info(f'Tổng số nhiệm vụ: {len(all_tasks)}')

            excluded_task_id = [
                "5daf7250-76cc-4851-ac44-4c7fdcfe5994",
                "3b0ae076-9a85-4090-af55-d9f6c9463b2b",
                "89710917-9352-450d-b96e-356403fc16e0",
                "220ee7b1-cca4-4af8-838a-2001cb42b813",
                "c4e04f2e-bbf5-4e31-917b-8bfa7c4aa3aa",
                "f382ec3f-089d-46de-b921-b92adfd3327a",
                "d3716390-ce5b-4c26-b82e-e45ea7eba258",
                "5ecf9c15-d477-420b-badf-058537489524",
                "d057e7b7-69d3-4c15-bef3-b300f9fb7e31",
                "a4ba4078-e9e2-4d16-a834-02efe22992e2",
                "39391eb2-f031-4954-bd8a-e7aecbb1f192",
                "d7accab9-f987-44fc-a70b-e414004e8314",
            ]
            
            # Lọc ra các nhiệm vụ chưa bắt đầu
            not_started_tasks = [task for task in all_tasks if task['id'] not in excluded_task_id and task['status'] != 'FINISHED' and not task['isHidden']]            

            logging.info(f'Số lượng nhiệm vụ chưa bắt đầu: {len(not_started_tasks)}')
            await self.getTaskKeywords()
            for task in not_started_tasks:
                if task["title"] != 'Farm' and task["title"] != 'Invite':
                    logging.info(f'Bắt đầu nhiệm vụ: {task["title"]}')

                    if await self.startTask(task['id']):
                        logging.info(f'Đã bắt đầu nhiệm vụ: {task["title"]}')
                    asyncio.sleep(4)

                    if task.get('validationType') == "KEYWORD":
                        keyword = self.task_keywords.get(task['id'])
                        if keyword:
                            validate_result = await self.validateTask(task['id'], keyword)
                            if not validate_result:
                                logging.info(f"Không thể xác thực nhiệm vụ: {task['title']}")
                        else:
                            logging.warning(f"Task {task['title']} chưa có câu trả lời nên bỏ qua")
                  
                    if (await self.claimTask(task['id'])).get('status') == 'FINISHED':
                        logging.info(f'Làm nhiệm vụ {task["title"]}... trạng thái: thành công!')
                    else:
                        logging.warning(f'Không thể nhận phần thưởng cho nhiệm vụ: {task["title"]}')
                    
    async def process_run_game(self):
        if self.balance_info and int(self.balance_info['playPasses']) > 0:
            for j in range(self.balance_info['playPasses']):
                play_attempts = 1
                max_attempts = 3

                while play_attempts < max_attempts:
                    try:
                        play_result = await self.playGame()
                        if play_result:
                            logging.info(f"Bắt đầu chơi game lần thứ {j + 1}...")
                            random_number = random.randint(250, 280)
                            await asyncio.sleep(30)
                            claim_game_result = await self.claimGame(random_number)
                            if claim_game_result:
                                logging.info(f"Đã nhận phần thưởng game lần thứ {j + 1} thành công!")
                            break
                        else:
                            raise Exception('Không thể bắt đầu trò chơi')
                    except Exception as error:
                        play_attempts += 1
                        logging.info(f"Không thể chơi game lần thứ {j + 1}, lần thử {play_attempts}: {error}")
                        if play_attempts < max_attempts:
                            logging.info("Đang thử lại sau 5 giây...")
                            await asyncio.sleep(5)
                        else:
                            logging.info(f"Đã thử {max_attempts} lần không thành công, bỏ qua lượt chơi này")
        
    async def getNewToken(self):
        url = 'https://user-domain.blum.codes/api/v1/auth/provider/PROVIDER_TELEGRAM_MINI_APP'
        data = {'query': self.query_id, 'referralToken': ""}

        for attempt in range(1, 3):
            response = await self.request_API.execute_post_request(url, data)
            if response:
                logging.info('Đăng nhập thành công!')
                self.token = response.get('token', {}).get('refresh')
                self.request_API.update_headers({'Authorization': f'Bearer {self.token}'})
                return True
            else:
                logging.error(f'Lỗi lấy token, thử lại ({attempt}/2)')
        return False

    async def getUserInfo(self):
        response = await self.request_API.execute_get_request('https://user-domain.blum.codes/api/v1/user/me')
        if response.get('username'):
            self.userInfo = response
            return self.userInfo
        else:
            if response and response.get('message') == 'Invalid jwt token':
                logging.warning('Token không hợp lệ, lấy token mới...')
                if await self.getNewToken():
                    logging.info('Lấy token mới thành công, đang thử lại...')
                    return await self.getUserInfo()
            logging.error('Không thể lấy thông tin người dùng.')
        return None

    async def getBalance(self):
        response = await self.request_API.execute_get_request('https://game-domain.blum.codes/api/v1/user/balance')       
        return response

    async def playGame(self):
        data = {'game': self.current_game_id}
        response = await self.request_API.execute_post_request('https://game-domain.blum.codes/api/v1/game/play', data)
        if response.get('gameId'):
            self.current_game_id = response.get('gameId')
            return True
        logging.error('Không thể chơi game.')
        return False
    
    async def claimGame(self, points):
        if not self.current_game_id:
            logging.error('Không có gameId để nhận phần thưởng.')
            return False
        data = {'gameId': self.current_game_id, 'points': points}
        response = await self.request_API.execute_post_request('https://game-domain.blum.codes/api/v1/game/claim', data)
        return response
    
    async def claimBalance(self):
        response = await self.request_API.execute_post_request('https://game-domain.blum.codes/api/v1/farming/claim')
        return response
    
    async def startFarming(self):
        response = await self.request_API.execute_post_request('https://game-domain.blum.codes/api/v1/farming/start')
        return response
    
    async def checkBalanceFriend(self):
        response = await self.request_API.execute_get_request('https://game-domain.blum.codes/api/v1/friend/balance')
        return response
    
    async def claimBalanceFriend(self):
        response = await self.request_API.execute_post_request('https://game-domain.blum.codes/api/v1/friend/claim')
        return response
    
    async def checkDailyReward(self):
        response = await self.request_API.execute_get_request('https://game-domain.blum.codes/api/v1/rewards/daily')
        if response.get('status') == 'AVAILABLE':
            return await self.claimDailyReward()
        return False
    
    async def claimDailyReward(self):
        response = await self.request_API.execute_post_request('https://game-domain.blum.codes/api/v1/rewards/claim', {})
        return response
    
    async def getTasks(self):
        response = await self.request_API.execute_get_request('https://earn-domain.blum.codes/api/v1/tasks')
        return response
    
    async def startTask(self, task_id):
        response = await self.request_API.execute_post_request(f'https://earn-domain.blum.codes/api/v1/tasks/start/{task_id}', {})
        return response
    
    async def claimTask(self, task_id):
        response = await self.request_API.execute_post_request(f'https://earn-domain.blum.codes/api/v1/tasks/claim/{task_id}', {})
        return response
    
    async def getTaskKeywords(self):
        try:
            response = await self.request_API.execute_get_request('https://raw.githubusercontent.com/dancayairdrop/blum/main/nv.json')
            data = response.get('data')

            if data and 'tasks' in data and isinstance(data['tasks'], list):
                self.task_keywords = {item['id']: item['keyword'] for item in data['tasks'] if 'id' in item and 'keyword' in item}
            else:
                self.task_keywords = {}
        except Exception as error:
            self.task_keywords = {}

    async def validateTask(self, taskId, keyword):
        data = {'keyword': keyword}
        response = await self.request_API.execute_post_request(f'https://earn-domain.blum.codes/api/v1/tasks/${taskId}/validate', data)
        return response
    
    async def getStatusTribe(self):
        response = await self.request_API.execute_get_request('https://game-domain.blum.codes/api/v1/tribes/status')
        return response
    
    async def joinTribes(self, tribe_id):
        response = await self.request_API.execute_post_request(f'https://game-domain.blum.codes/api/v1/tribes/join/{tribe_id}', {})
        return response