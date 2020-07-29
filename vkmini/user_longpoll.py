import requests
import logging
from . import VkApi
from datetime import datetime

# from wtflog import warden
# logger = warden.get_boy('VK Group LongPoll')
from .printer import Printer
logger = Printer()

class LP():

    key: str
    server:str
    ts: int
    receive_time: float
    vk: VkApi
    wait: int

    def __init__(self, vk, wait = 25):
        self.vk = vk
        data = vk('messages.getLongPollServer')
        if data.get('error'):
            if data['error']['error_code'] == 5:
                raise Exception('tokenfail')
        self.server = data['server']
        self.key = data['key']
        self.ts = data['ts']
        self.wait = wait

    @property
    def check(self):
        response = requests.get(f"http://{self.server}?act=a_check&key={self.key}&ts={self.ts}&wait={self.wait}&mode=2&version=10")

        if response.status_code != 200:
            return []

        self.receive_time = datetime.now().timestamp()
        data = response.json()

        if 'failed' in data.keys():
            if data['failed'] == 1:
                logger.error('Ошибка истории событий')
                self.ts = data['ts']
            elif data['failed'] == 2:
                self.key = self.vk('messages.getLongPollServer')['key']
            else:
                raise Exception('Информация о пользователе утрачена')
            return []
        else:
            self.ts = data['ts']
            return data['updates']
