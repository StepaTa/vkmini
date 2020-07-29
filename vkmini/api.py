# давай вот щас не начинай, работает, а больше мне ничего не нужно
import requests
from .methods import Messages
from time import sleep

# from wtflog import warden
# logger = warden.get_boy('VK API')
from .printer import Printer
logger = Printer()

class VkApiResponseException(Exception):# да, спиздил))0)
    def __init__(self, *args, **kwargs):
        self.error_code = kwargs.get('error_code', None)
        self.error_msg = kwargs.get('error_msg', None)
        self.request_params = kwargs.get('request_params', None)

        self.args = args
        self.kwargs = kwargs


class VkApi:
    url: str = 'https://api.vk.com/method/'
    query: str
    excepts: bool

    messages = Messages

    def __init__(self, access_token: str, excepts: bool = False, version: str = "5.110"):
        'Eсли excepts == True, ошибки ВК будут генерировать исключение VkApiResponseException'
        self.query = f'?v={version}&access_token={access_token}&lang=ru'
        self.excepts = excepts

    def __call__(self, method, **kwargs):
        logger.debug(f'URL = "{self.url}{method}{self.query}" Data = {kwargs}')
        r = requests.post(f'{self.url}{method}{self.query}', data = kwargs)
        if r.status_code == 200:
            r = r.json()
            if 'response' in r.keys():
                logger.info(f"Запрос {method} выполнен")
                return r['response']
            elif 'error' in r.keys():
                logger.warning(f"Запрос {method} не выполнен: {r['error']}")
                if self.excepts:
                    if r['error']['error_code'] == 5:
                        raise Exception('tokenfail')
                    if r['error']['error_code'] == 6:
                        raise Exception('toomanyrequests')
                    else:
                        raise VkApiResponseException(**r["error"])
            return r
        elif self.excepts:
            raise Exception('networkerror')

    def method(self, method, **kwargs):
        return self.__call__(method, **kwargs)

    def msg_op(self, mode: int, peer_id: int = 0, text: str = '',
               msg_id: int = 0, delete_delay: float = 0, **kwargs):
        '''`mode` 1 - отправка, 2 - редактирование, 3 - удаление, 4 - удаление только для себя\n
        Если указан параметр `delete_delay` - сообщение удалится через указанное количество секунд'''
        if mode == 4:
            mode = 3
            dfa = 0
        else: dfa = 1

        mode = ['messages.send', 'messages.edit', 'messages.delete'][mode - 1]
        
        response = self(mode, peer_id = peer_id, message = text,
        message_id = msg_id, delete_for_all = dfa, random_id = 0, **kwargs)
        if delete_delay:
            sleep(delete_delay)
            if mode == 1: msg_id = response
            self('messages.delete', message_id = msg_id, delete_for_all = 1)
        return response
            
    def exe(self, code, alt_token = ''):
        '''Метод execute\n
        Если указан `alt_token`, запрос будет отправлен с указанным токеном'''
        if alt_token:
            return VkApi(alt_token, self.excepts)('execute', code = code)
        else:
            return self('execute', code = code)