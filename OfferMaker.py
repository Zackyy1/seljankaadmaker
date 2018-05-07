import telebot
from telebot import types
import tempdb
import passwords
global stage
stage = 0
token = '571706625:AAHizahsSPrKZWjUVfkjtU_Zu14iEN_YBEo'
db = tempdb.db
bot = telebot.TeleBot(token)

pw = passwords.passwords

def checkforPassword(text):
    print("Searching for password match...")
    keys = list(pw.keys())
    values = list(pw.values())
    print(keys, values)
    who = ""
    for i in range(0, len(pw)):
        if text in values[i]["pass"]:
            print("Found password by: "+str(keys[i]))
            who = str(keys[i])
    if who != "":
        return who
    else:
        print("Password incorrect")
        return None

def setStage(stagenum, mes):
    global stage
    stage = stagenum

def newButton(*args):
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
    mass = []
    for arg in args:
        but = types.KeyboardButton(arg)
        mass.append(but)
    markup.add(*mass)
    return markup

def findKey(dict, key):
    keys = list(dict.keys())
    values = list(dict.values())
    for i in range(0, len(db)):
        if str(keys[i]) in values:
            return True
        else:
            return False

@bot.message_handler(commands=["start"])
def handle_start(mes):
    bot.send_message(mes.chat.id, "Send me password. I will reply only if you have a password for your restaurant")
    setStage(1, mes)

@bot.message_handler(content_types=["text"])
def handle_Messages(mes):
    global stage
    if stage == 1:
        init = str(checkforPassword(mes.text))
        if init != None:
            db[init]["user"] = mes.chat.id
            setStage(2, mes)
    elif stage == 2:
        print("Found 'USER'? "+findKey(db, "user"))
    else:
        print("Couldnt find stage...")


bot.polling()