import telebot
from firebase import firebase
from telebot import types
import tempdb
from random import randint
import random
from flask import jsonify
from flask import Flask
from flask import request
import redis
import requests
import re
import json
import os

tempdb.db = {}
print(tempdb.db)
passwords = {
    "steffani":"abcde",
    "wesset":"pepe"
}
CITY = "offersparnu"

token = os.environ['TELEGRAM_TOKEN']
url = os.environ['FIREBASE_URL']
server = Flask(__name__)

fb = firebase.FirebaseApplication(url, None)
bot = telebot.TeleBot(token)

######################################################################################### FUNCTIONS ####################


def inline(*args):
    markup = types.InlineKeyboardMarkup()
    for arg1, arg2 in args:
        markup.add(types.InlineKeyboardButton(text=arg1, callback_data=arg2))
    return markup

def check(who):
    if who in tempdb.db:
        print("Is in, look!")
        print(tempdb.db)
        return True
    else:
        print("Nothing found :(")
        return False

def newBut(*args):
    mrkup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True,resize_keyboard=True)
    tr = []
    for arg in args:
        b = types.KeyboardButton(arg)
        tr.append(b)
    mrkup.add(*tr)
    return mrkup

def findKey(mes, key):
    whattoreturn = False
    keys = list(tempdb.db[getDict(mes)].keys())
    for i in range(0, len(tempdb.db[getDict(mes)])):
        if keys[i] == key:
            whattoreturn = True
    print(whattoreturn)
    return whattoreturn


def identify(mes, whattofind):
    keys = list(tempdb.db.keys())
    values = list(tempdb.db.values())
    whattoreturn = False
    for i in range(0, len(tempdb.db)):
        print("Searching..."+str(values[i]))
        if str(mes.chat.id) == values[i][whattofind]:
            print("Found!")
            whattoreturn = True
        else:
            whattoreturn = False
    return whattoreturn

def ident(mes):
    keys = list(tempdb.db.keys())
    toreturn = False
    for i in range(0, len(tempdb.db)):
        if keys[i] == str(mes.chat.id):
            toreturn = True
        else:
            toreturn = False
    return toreturn


def getDict(mes):
    keys = list(tempdb.db.keys())
    values = list(tempdb.db.values())
    for i in range(0, len(tempdb.db)):
        if str(mes.chat.id) == str(keys[i]):
            #print("Dict: "+str(keys[i]))
            print("Found: "+str(keys[i]))
            return keys[i]
        else:
            return


def finish(mes):
    print("Finishing setup")

######################################################################################### HANDLERS #####################

@bot.message_handler(commands=["start"])
def start_init(mes):
    tempdb.db[mes.chat.id] = {}
    bot.send_message(mes.chat.id, "To send an offer, send me your given password. I will respond when you enter the correct password", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=["done"])
def done_init(mes):
    tempdb.db[getDict(mes)]['isDone'] = True
    tempdb.db[getDict(mes)]['image'] = ""
    bot.send_message(mes.chat.id, "Do you want to publish the following?:", reply_markup=newBut("Yes, publish", "No, restart."))
    bot.send_photo(mes.chat.id, photo=tempdb.db[getDict(mes)]['desc'])


@bot.callback_query_handler(func=lambda call : True)
def query_answer(call):
    print(call.data)
    if call.data == 'text':
        bot.send_message(call.message.chat.id, """Send me your advertisement description.
You can include any information as long as it is related to your restaurant, i.e. dicounts, events, date.""")
@bot.message_handler(content_types=['text'])
def register_password(mes):
    pkeys = list(passwords.keys())
    pvalues = list(passwords.values())
    keys = list(tempdb.db.keys())
    values = list(tempdb.db.values())
    #did = identify(mes, 'id')
    did = ident(mes)
    if did == False:
        print("Searching for password")
        for i in range(0, len(passwords)):
            if mes.text in pvalues[i]:
                print("GUCCI! Organiser:"+str(pkeys[i]))
                check(str(pkeys[i]))
                tempdb.db[str(mes.chat.id)] = {}
                tempdb.db[str(mes.chat.id)]["isDone"] = False
                print("Added "+str(pkeys[i])+" to temp database. Can send photo/text now.")
                check(str(pkeys[i]))
                bot.send_message(mes.chat.id, "Enter description", reply_markup=types.ForceReply(selective=False))

    elif did == True and findKey(mes, 'desc') == False:
        print("Person is in database, can send description")
        tempdb.db[getDict(mes)]['desc'] = mes.text
        bot.send_message(mes.chat.id, "Now you can send a picture! It must be a link to any image hosting website, or your own website and must end with .jpeg or .jpg. If you don't have a picture, or it is just text advertisement, type /done")

    elif did == True and findKey(mes, 'desc') == True and findKey(mes, "isDone") == True and tempdb.db[str(mes.chat.id)]["isDone"] == False:
        tempdb.db[getDict(mes)]["isDone"] = True
        tempdb.db[getDict(mes)]["image"] = mes.text
        print("User submitted picture. URL: "+mes.text)
        bot.send_message(mes.chat.id, "Do you want to publish the following?:")
        try:
            bot.send_photo(mes.chat.id, photo=tempdb.db[getDict(mes)]['image'])
        except Exception as x:
            print(x)
            bot.send_message(mes.chat.id, "This URL is invalid. Please restart and send another one with extension .jpeg or .jpg.")
            tempdb.db[getDict(mes)]["image"] = ""
        bot.send_message(mes.chat.id, tempdb.db[getDict(mes)]['desc'], reply_markup=newBut("Yes, publish", "No, restart."))

    elif mes.text == "Yes, publish" and tempdb.db[getDict(mes)]["isDone"] == True:
        bot.send_message(mes.chat.id, "Published. For another ad, type /start")
        tempdb.db[getDict(mes)]['toPublish'] = {}
        tempdb.db[getDict(mes)]['toPublish']['desc'] = tempdb.db[getDict(mes)]['desc']
        if tempdb.db[getDict(mes)]['image'] != "":
            tempdb.db[getDict(mes)]['toPublish']['image'] = tempdb.db[getDict(mes)]['image']
        print(tempdb.db[getDict(mes)]['toPublish'])
        fb.patch(url+"/"+CITY+"/"+str(randint(10000000,99999999)), tempdb.db[getDict(mes)]['toPublish'])

    elif mes.text == "No, restart." and tempdb.db[getDict(mes)]["isDone"] == True:
        tempdb.db[getDict(mes)] = {}
        tempdb.db[str(mes.chat.id)]["id"] = str(mes.chat.id)
        tempdb.db[str(mes.chat.id)]["isDone"] = False
        bot.send_message(mes.chat.id, "Enter description", reply_markup=types.ForceReply(selective=False) )




@bot.message_handler(content_types=['photo'])
def photo_handler(mes):
    #if identify(mes) == True:
        print("Came from: "+str(getDict(mes)))
        print(mes.photo[0].file_id)
        tempdb.db[getDict(mes)]["image"] = mes.photo[0].file_id
        path2 = bot.get_file(mes.photo[0].file_id)
        print(tempdb.db)
        print(path2.file_path)
        path = path2.file_path



########################################################################################################################


@server.route('/' + token, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://seljankaadmaker.herokuapp.com/' + token)
    return "!", 200


if __name__ == "__main__":
    try:
        server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
    except Exception as x:
        print(x)
