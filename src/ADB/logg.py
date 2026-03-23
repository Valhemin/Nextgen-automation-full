import threading
import os
import re
from datetime import datetime
from colorama import Fore, Style, init


class Logg(object):
    def __init__(self):
        if not os.path.exists('./logs'):
            os.makedirs('./logs')
        self._name = os.path.join('./logs', f'{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.txt')
        self._lock = threading.Lock()
        init(autoreset=True)

    def _print(self, txt: str, color: str):
        with self._lock:
            print(f"{color}{txt}{Style.RESET_ALL}")
            with open(self._name, 'a+', encoding="utf-8") as f:
                f.write(f'{txt}\n')

    def print(self, txt: str):
        with self._lock:
            print(txt)
            cleaned = re.sub('\[[0-9;]+[a-zA-Z]', ' ', txt)
            with open(self._name, 'a+', encoding="utf-8") as f:
                f.write(f'{cleaned}\n')

    def success(self, txt: str):
        self._print(txt, Fore.LIGHTBLUE_EX)

    def error(self, txt: str):
        self._print(txt, Fore.LIGHTRED_EX)

    def info(self, txt: str):
        self._print(txt, Fore.WHITE)

    def warning(self, txt: str):
        self._print(txt, Fore.LIGHTYELLOW_EX)