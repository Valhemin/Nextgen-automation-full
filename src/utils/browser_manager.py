import psutil
import pyautogui
import time
import socket
import random
from .global_variable_manager import GlobalVariableManager


class BrowserManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BrowserManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        pass
        
    @staticmethod
    def get_screen_size() -> tuple[int, int]:
        return pyautogui.size()
    
    @staticmethod
    def calculate_optimal_layout(screen_width: int, screen_height: int, first_win_size: tuple[int, int], 
                                  num_profiles: int, max_workers: int, min_size: tuple[int, int] = (200, 300)) -> dict:
        # Khoảng cách giữa các cửa sổ
        offset = 10

        # Tính toán không gian còn lại sau khi đặt profile đầu tiên
        remaining_width = screen_width - first_win_size[0] - offset

        # Tính số lượng profile tối đa trên một hàng ngang
        max_profiles_per_row = min(max(1, remaining_width // (max(first_win_size[0], min_size[0]) * 0.5 + offset)), max_workers)

        # Tính số hàng cần thiết
        num_rows = (num_profiles + max_profiles_per_row - 1) // max_profiles_per_row

        # Tính kích thước tối ưu cho các profile từ thứ hai trở đi
        if num_rows > 0:
            optimal_width = max((remaining_width - (max_profiles_per_row - 1) * offset) // max_profiles_per_row, min_size[0])  # Đảm bảo không nhỏ hơn kích thước tối thiểu
            optimal_height = max((screen_height - (num_rows - 1) * offset) // num_rows, min_size[1])  # Đảm bảo không nhỏ hơn kích thước tối thiểu
        else:
            optimal_width = min_size[0]
            optimal_height = min_size[1]

        return {
            'max_profiles_per_row': int(max_profiles_per_row),
            'optimal_size': (optimal_width, optimal_height)
        }

    @staticmethod
    def calculate_window_layout(profiles_selected: list[dict], max_workers: int, min_size: tuple[int, int] = (200, 400)) -> list[dict]:
        num_profiles = len(profiles_selected)
        screen_width, screen_height = BrowserManager.get_screen_size()

        window_configurations = []

        # Kích thước cố định cho profile đầu tiên
        first_win_size = (400, 600)
        optimal_layout = BrowserManager.calculate_optimal_layout(screen_width, screen_height, first_win_size, num_profiles, max_workers, min_size)
        max_profiles_per_row = optimal_layout['max_profiles_per_row']
        second_batch_size = optimal_layout['optimal_size']

        # Độ lệch giữa các profile
        offset_x = 10
        offset_y = 10

        # Chia các profile thành các nhóm dựa trên max_workers
        for batch_start in range(0, num_profiles, max_workers):
            current_batch = profiles_selected[batch_start:batch_start + max_workers]

            # Cấu hình cho profile đầu tiên trong nhóm
            if current_batch:
                first_win_size = (min(first_win_size[0], screen_width), min(first_win_size[1], screen_height))
                window_configurations.append({
                    'id': current_batch[0]['id'],
                    'winScale': 1,
                    'winPos': "0,0",
                    'winSize': f"{first_win_size[0]},{first_win_size[1]}"
                })

                # Tính toán vị trí cho các profile tiếp theo
                current_x = first_win_size[0] + offset_x
                current_y = 0
                profiles_in_current_row = 0

                # Xử lý các profile tiếp theo trong nhóm
                for i in range(1, len(current_batch)):
                    # Kiểm tra nếu đã đạt số profile tối đa trên một hàng
                    if profiles_in_current_row >= max_profiles_per_row:
                        current_x = first_win_size[0] + offset_x  # Đặt về đầu dòng nhưng vẫn cách profile đầu tiên
                        current_y += second_batch_size[1] + offset_y  # Xuống hàng
                        if current_y >= first_win_size[1]:
                            current_x = 0
                        profiles_in_current_row = 0

                    # Đảm bảo không vượt quá chiều cao màn hình
                    if current_y + second_batch_size[1] > screen_height:
                        break  # Nếu không còn không gian, thoát khỏi vòng lặp

                    # Tính toán kích thước cho profile tiếp theo
                    win_size = (
                        max(min_size[0], second_batch_size[0]),
                        max(min_size[1], second_batch_size[1])
                    )

                    # Tính toán vị trí cho profile tiếp theo
                    win_pos = (current_x, current_y)

                    # Thêm cấu hình cho profile
                    window_configurations.append({
                        'id': current_batch[i]['id'],
                        'winScale': 0.4,  # Tỷ lệ nhỏ hơn cho các profile tiếp theo
                        'winPos': f"{win_pos[0]},{win_pos[1]}",
                        'winSize': f"{win_size[0]},{win_size[1]}"
                    })

                    # Cập nhật vị trí x cho profile tiếp theo và đếm số profile trong hàng hiện tại
                    current_x += win_size[0]
                    profiles_in_current_row += 1

        return window_configurations

    @staticmethod
    def kill_process_by_pid(pid: int) -> None:
        try:
            process = psutil.Process(pid)
            process.terminate()
            print(f"Process with PID {pid} has been terminated.")
        except psutil.NoSuchProcess:
            print(f"No process found with PID {pid}.")

    @staticmethod
    def get_random_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(('', 0))
            port = sock.getsockname()[1]
        return port
