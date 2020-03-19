import json

import vk_api
from flask import Flask, request, jsonify

# --------------------------------------------
token = "ТОКЕН"                          # ---
secret = "КОРОТКИЙ КЛЮЧ ДЛЯ ЮЗЕР-БОТА'а" # ---
# --------------------------------------------


app = Flask(__name__)
vk = vk_api.VkApi(token=token)


def add_fr(user):
    vk.method('friends.add', {'user_id': user})


def del_fr(user):
    vk.method('friends.delete', {'user_id': user})


def invite_user(chat, user):
    vk.method('messages.addChatUser', {'chat_id': chat, 'user_id': user})


def delete_msg(chat_id, msg_ids):
    vk.method('messages.delete', {'message_ids': get_conv_msg_ids(chat_id, msg_ids), 'delete_for_all': 1})


def get_peer_id(chat_id):
    peer_id = int(chat_id) + 2000000000
    return peer_id


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
    if data.get('secret_key') == secret:
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

            elif task == 'add_fr':
                add_fr(object['user'])
                write_msg(object['chat_id'],"&#9989; Заявка дружбы была отправлена")
                return jsonify(response=1)

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
        return jsonify(response=2)



# ошибка №2 - неверный ключ
# ошибка №4 - пользователь не в друзьях
# ошибка №5 - внутренняя ошибка вк, тут остаётся только ждать и верить в лучшее
# ошибка №6 - неверный токен
# ошибка №7 - У вас слишком перегружен сервер, не раздавайте свой сервер кому попало
# ошибка №0 - страшная ошибка никому неизвестная
