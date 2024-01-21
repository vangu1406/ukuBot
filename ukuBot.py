import telebot
from telebot import apihelper
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import xml.etree.ElementTree as ET

TOKEN = ''  # Enter your token
bot = telebot.TeleBot(TOKEN, parse_mode="markdown")

class ChordInput:
    def __init__(self):
        self.root_note = None
        self.chord_type = None

user_input = ChordInput()

VALID_NOTES = ["A", "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab"]
VALID_CHORD_TYPES = ["major", "m", "aug", "dim", "7", "m7", "maj7", "m7b5", "sus2", "sus4", "7sus4", "9", "11", "13", "6", "m6", "add9", "m9", "5", "dim7", "m13", "7sus2", "mMaj7", "m11", "maj9"]

@bot.message_handler(content_types=["text"])
def handle_message(message):
    chat_id = message.chat.id
    try:
        bot.send_message(chat_id, f"*Enter the root note of the chord. Choose from*: {', '.join(VALID_NOTES)}")
        bot.register_next_step_handler(message, process_root_note)
    except apihelper.ApiException as e:
        print(f"ApiException: {e}")

def process_root_note(message):
    if message.text == "/start":
        return handle_message(message)

    chat_id = message.chat.id
    user_input.root_note = message.text

    if user_input.root_note not in VALID_NOTES:
        try:
            bot.send_message(chat_id, f"*Invalid note. Please enter a valid note from*: {', '.join(VALID_NOTES)}")
            bot.register_next_step_handler(message, process_root_note)
        except apihelper.ApiException as e:
            print(f"ApiException: {e}")
    else:
        try:
            bot.send_message(chat_id, f"*Enter a type of chord. Choose from*: {', '.join(VALID_CHORD_TYPES)}")
            bot.register_next_step_handler(message, process_chord_type)
        except apihelper.ApiException as e:
            print(f"ApiException: {e}")

def process_chord_type(message):
    if message.text == "/start":
        return handle_message(message)

    chat_id = message.chat.id
    user_input.chord_type = message.text

    if user_input.chord_type not in VALID_CHORD_TYPES:
        try:
            bot.send_message(chat_id, f"*Invalid type. Please enter a valid type from*: {', '.join(VALID_CHORD_TYPES)}")
            bot.register_next_step_handler(message, process_chord_type)
        except apihelper.ApiException as e:
            print(f"ApiException: {e}")
    else:
        try:
            api_url = f"http://www.ukulele-chords.com/get?ak=YOUR_API_KEY&r={user_input.root_note}&typ={user_input.chord_type}"
            req = Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
            data = urlopen(req).read()
            root = ET.fromstring(data)
            chord_image_url = root[0][2].text
            bot.send_photo(chat_id, photo=chord_image_url)
            handle_message(message)
        except HTTPError as err:
            if err.code == 404:
                bot.send_message(chat_id, "Data not found")


if __name__ == "__main__":
    bot.polling(none_stop=True)