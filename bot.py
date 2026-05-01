import requests
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "YOUR_BOT_TOKEN_HERE"

# Flask app (for Render port)
app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot is running"

def run_web():
    app_web.run(host="0.0.0.0", port=10000)

# user mode
user_mode = {}

# Myanmar dictionary
mm_dict = {
    "run": "ပြေးသည် / လည်ပတ်သည်",
    "eat": "စားသည်",
    "go": "သွားသည်",
    "love": "ချစ်သည်",
}

# dictionary function
def get_word_data(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    res = requests.get(url)

    if res.status_code != 200:
        return None

    data = res.json()[0]
    result = f"📖 Word: {word}\n\n"

    if word in mm_dict:
        result += f"🇲🇲 {mm_dict[word]}\n\n"

    for m in data["meanings"]:
        result += f"🔹 {m['partOfSpeech']}\n"
        for d in m["definitions"][:2]:
            result += f"- {d['definition']}\n"
        result += "\n"

    return result

# start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📖 Dictionary", "🌐 Translate"]]
    await update.message.reply_text("Choose mode", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# message
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    data = get_word_data(text)

    if data:
        await update.message.reply_text(data)
    else:
        await update.message.reply_text("❌ Not found")

# run bot
def run_bot():
    app = ApplicationBuilder().token("8618858114:AAG1MJQxqPdxjgCN3NRENWTKEbbPGf1o5m4").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle))
    app.run_polling()

# threading run
if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
