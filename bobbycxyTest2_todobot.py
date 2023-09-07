# bobbycxyTest2.py
# Resource: 
# Part 1: https://www.codementor.io/@garethdwyer/building-a-telegram-bot-using-python-part-1-goi5fncay
# Part 2: https://www.codementor.io/@garethdwyer/building-a-chatbot-using-telegram-and-python-part-2-sqlite-databse-backend-m7o96jger



from bobbycxyTest2_dbhelper import DBHelper

db = DBHelper()

import json 
import requests
import time
import urllib

TOKEN = ##insert token##
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

# response = requests.get(URL + 'getUpdates')
# content = response.text
# js = json.loads(content)
# js = response.json()
# len(js['result'])
# chat_id = js['result'][1]['message']['chat']['id']
# js['result'][1]['message']['text']


##############



def get_url(url):
    '''This will execute the url. It will return a content in the form of a JSON output.'''
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    '''This converts the JSON output of the get_url function into a python object. This is known as deserialisation.'''
    content = get_url(url)
    js = json.loads(content)
    return js


# def get_updates():
#     '''Using the get_json_from_url function, this will retrieve the updates that get sent to out bot.'''
#     url = URL + "getUpdates"
#     js = get_json_from_url(url)
#     return js

# def get_updates(offset=None):
#     url = URL + "getUpdates"
#     if offset:
#         url += "?offset={}".format(offset)
#     js = get_json_from_url(url)
#     return js

def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

###
len(get_updates()['result'])
###


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def get_last_chat_id_and_text(updates):
    '''This returns the chat_id and text of the latest sent message to our chatbot.'''
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard":True}
    return json.dumps(reply_markup)

# def send_message(text, chat_id):
#     text = urllib.parse.quote_plus(text)
#     url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
#     get_url(url)

def send_message(text, chat_id, reply_markup = None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += '&reply_markup={}'.format(reply_markup)
    get_url(url)

#### DELETE THIS - because we're now replacing it with 'handle_updates' ####
# def echo_all(updates):
#     for update in updates["result"]:
#         try:
#             text = update["message"]["text"]
#             chat = update["message"]["chat"]["id"]
#             send_message(text, chat)
#         except Exception as e:
#             print(e)

# def handle_updates(updates):
#     for update in updates["result"]:
#         try:
#             text = update["message"]["text"]
#             chat = update["message"]["chat"]["id"]
#             items = db.get_items()
#             if text in items:
#                 db.delete_item(text)
#                 items = db.get_items()
#             else:
#                 db.add_item(text)
#                 items = db.get_items()
#             message = "\n".join(items)
#             send_message(message, chat)
#         except KeyError:
#             pass

def handle_updates(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        items = db.get_items()
        if text == "/done":
            keyboard = build_keyboard(items)
            send_message("Select an item to delete", chat, keyboard)
        elif text in items:
            db.delete_item(text)
            items = db.get_items()
            keyboard = build_keyboard(items)
            send_message("Select an item to delete", chat, keyboard)
        else:
            db.add_item(text)
            items = db.get_items()
            message = "\n".join(items)
            send_message(message, chat)



def main():
    db.setup()
    last_update_id = None
    while True:
        print("getting updates")
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)
        


if __name__ == '__main__':
    main()
