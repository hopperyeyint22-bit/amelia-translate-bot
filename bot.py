import requests
import json
import threading
import os
from flask import Flask
from gtts import gTTS
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8618858114:AAG1MJQxqPdxjgCN3NRENWTKEbbPGf1o5m4"

# 📦 load dictionary
with open("mm_dict.json", "r", encoding="utf-8") as f:
    mm_dict = json.load(f)

# 🌐 Flask for Render port
app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot is running ✔"

def run_web():
    app_web.run(host="0.0.0.0", port=10000)

# user mode
user_mode = {}

# 📚 dictionary API
def get_word_data(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    res = requests.get(url)

    if res.status_code != 200:
        return None

    data = res.json()[0]

    result = f"📖 Word: {word}\n\n"

    # 🇲🇲 Myanmar meaning
    if word in mm_dict:
        result += f"🇲🇲 Myanmar: {mm_dict[word]}\n\n"

    # pronunciation
    if "phonetic" in data:
        result += f"🔊 Pronunciation: {data['phonetic']}\n\n"

    for m in data["meanings"]:
        result += f"🔹 {m['partOfSpeech']}\n"
        for d in m["definitions"][:2]:
            result += f"- {d['definition']}\n"
        result += "\n"

    return result

# 🔊 voice
def make_voice(text):
    tts = gTTS(text=text, lang="en")
    file = "voice.mp3"
    tts.save(file)
    return file

# 🚀 start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📖 Dictionary", "🌐 Translate"]]
    await update.message.reply_text(
        "👋 Welcome!",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# 💬 handler
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if text == "📖 dictionary":
        user_mode[update.effective_user.id] = "dict"
        await update.message.reply_text("📖 Dictionary mode")
        return

    if text == "🌐 translate":
        user_mode[update.effective_user.id] = "trans"
        await update.message.reply_text("🌐 Translate mode")
        return

    mode = user_mode.get(update.effective_user.id, "dict")

    if mode == "dict":
        data = get_word_data(text)
        if data:
            await update.message.reply_text(data)

            # 🔊 voice
            voice = make_voice(text)
            await update.message.reply_voice(voice=open(voice, "rb"))
            os.remove(voice)
        else:
            await update.message.reply_text("❌ Not found")

    else:
        res = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": text, "langpair": "en|my"}
        )
        result = res.json()["responseData"]["translatedText"]
        await update.message.reply_text(f"🌐 {result}")

# 🌐 run flask + bot
if __name__ == "__main__":
    threading.Thread(target=run_web).start()

    app = ApplicationBuilder().token("8618858114:AAG1MJQxqPdxjgCN3NRENWTKEbbPGf1o5m4").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle))

    print("Bot running...")
    app.run_polling()
