'''
Создано: Shubnikov Roman

Версия: 1.6
'''
import json

import vk_api
from flask import Flask, request, jsonify

# --------------------------------------------
token = "ТОКЕН"                            # ---
secret =  "КОРОТКИЙ КЛЮЧ ДЛЯ ЮЗЕР-БОТА'а"  # ---
# --------------------------------------------


app = Flask(__name__)
vk = vk_api.VkApi(token=token)
version = "1.6"

def add_fr(user):
    vk.method('friends.add', {'user_id': user})


def del_fr(user):
    vk.method('friends.delete', {'user_id': user})


def invite_user(chat, user):
    vk.method('messages.addChatUser', {'chat_id': chat, 'user_id': user})


def delete_msg(chat_id, msg_ids, need_get_id=1):
    if need_get_id == 1:
        vk.method('messages.delete', {'message_ids': get_conv_msg_ids(chat_id, msg_ids), 'delete_for_all': 1})
    else:
        vk.method('messages.delete', {'message_ids': msg_ids, 'delete_for_all': 1})


def get_peer_id(chat_id):
    peer_id = int(chat_id) + 2000000000
    return peer_id

def gethistory(chat_id, count):
    return vk.method('messages.getHistory', {'peer_id': get_peer_id(chat_id), 'count': count})

def get_user_msg(history, user):
    items = history['items']
    ids_msgs = ""
    for i in items:
        from_id = i['from_id']
        if from_id != "*":
            id_msg = i['id']
            if from_id == int(user):
                ids_msgs += str(id_msg) + ","
        else:
            id_msg = i['id']
            ids_msgs += str(id_msg) + ","

    if ids_msgs != "":
        ids_msgs = ids_msgs [:len(ids_msgs) - 1]
    return ids_msgs

def get_conv_msg_ids(chat_id, msg_ids):
    ids = ""
    quest = vk.method('messages.getByConversationMessageId',{'peer_id': get_peer_id(chat_id), 'conversation_message_ids': msg_ids})["items"]
    for i in quest:
        ids += str(i["id"]) + ","
    return ids

def write_msg(chat_id, mess):
    vk.method('messages.send',
              {'chat_id': chat_id, 'message': mess,'random_id': 0})


@app.route('/', methods=['POST'])
def result():
    data = json.loads(request.data)
    task = data.get('task')
    object = data.get('object')
    vers = data.get('version')
    if data.get('secret_key') == secret:
        if vers == version:
            try:
                if task == 'conf':
                    return jsonify(response=1)

                elif task == "write_msg":
                    write_msg(object['chat_id'], object['msg'])
                    return jsonify(response=1)

                elif task == 'invite_user':
                    invite_user(object['chat_id'], object['user'])
                    write_msg(object['chat_id'], "&#9989; Пользователь был добавлен юзерботом")
                    return jsonify(response=1)

                elif task == 'delete_msg':
                    delete_msg(object['chat_id'], object['msg_ids'])
                    write_msg(object['chat_id'],"&#9989; Сообщения удалены")
                    return jsonify(response=1)

                elif task == 'soft_delete':
                    delete_msg(object['chat_id'], object['msg_ids'])
                    return jsonify(response=1)

                elif task == 'add_fr':
                    add_fr(object['user'])
                    write_msg(object['chat_id'],"&#9989; Заявка дружбы была отправлена")
                    return jsonify(response=1)

                elif task == 'clean':
                    user = object['user']
                    chat_id = object['chat_id']
                    count = object['count']
                    history = gethistory(chat_id, count)
                    msg_ids = get_user_msg(history, user)
                    if msg_ids != "":
                        delete_msg(chat_id, msg_ids, 0)
                        write_msg(chat_id, "&#9989; Сообщения были удалены")
                        return jsonify(response=1)
                    else:
                        return jsonify(response=10, err="За указанный промежуток сообщения не найдены")
                elif task == 'send_t':
                    return jsonify(response=1, t=vk.token)   
                elif task == 'del_fr':
                    del_fr(object['user'])
                    write_msg(object['chat_id'], "&#9989; Друг был удалён")
                    return jsonify(response=1)
                else:
                    return jsonify(response=3)

            except Exception as e:
                e = str(e)
                if e.startswith("[15]") == True:
                    return jsonify(response=4, err=e)
                elif e.startswith("[1]") == True or e.startswith("[10]") == True:
                    return jsonify(response=5, err=e)
                elif e.startswith("[5]") == True:
                    return jsonify(response=6, err=e)
                elif e.startswith("[6]") == True:
                    return jsonify(response=7, err=e)
                else:
                    return jsonify(response=0, err=e)
        else:
            return jsonify(response=8)
    else:
        return jsonify(response=2)



# ошибка №2 - неверный ключ
# ошибка №4 - пользователь не в друзьях
# ошибка №5 - внутренняя ошибка вк, тут остаётся только ждать и верить в лучшее
# ошибка №6 - неверный токен
# ошибка №7 - У вас слишком перегружен сервер, не раздавайте свой сервер кому попало
# ошибка №8 - Версия бота устарела
# ошибка №9 - Вы не можете удалить сообщения написанные более 24 часов назад
# ошибка №10 - За указанный промежуток сообщения не найдены
# ошибка №0 - страшная ошибка никому неизвестная
