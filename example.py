from vkmini import VkApi, LP
from datetime import datetime

token = '<VK token>'
me_token = '<VK Me token>'

vk = VkApi(token)

lp = LP(vk)

def handle(update):
    text_lowered = update[5].lower()
    if text_lowered == 'тест':
        vk.msg_op( # отправка нового сообщения
            mode = 1,
            peer_id = update[3],
            text = f'''Хэй!\nСообщение получено через {
            round(lp.receive_time - update[4], 1)
            }с. (±0.5)'''
            )
    elif text_lowered == 'скрин':
        # отправка execute запроса
        vk.exe(
            '''return API.messages.sendService({
            peer_id:%s,
            action_type:"chat_screenshot",
            random_id:0
            });''' % update[3], me_token)
        # редактирование сообщения с последующим его удалением через 3 секунды
        # компактный вид:
        # vk.msg_op(2, update[3], 'Запрос отправлен!', update[1], 3)
        vk.msg_op(
            mode = 2,
            peer_id = update[3],
            text = 'Запрос отправлен!',
            msg_id = update[1],
            delete_delay = 3
            )

while True:
    for update in lp.check: # проверка событий пользовательского longpoll
        if update[0] == 4 and update[2] & 2 == 2:
            handle(update)