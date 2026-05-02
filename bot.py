import requests
import json
import threading
import os
import asyncio
from flask import Flask
from gtts import gTTS
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🔐 TOKEN (Render env variable)
TOKEN = os.getenv("8618858114:AAE9oPIuTl_tH5FWVEwlwgkOw8APBsFjeg8")

# 📦 load dictionary
with open("mm_dict.json", "r", encoding="utf-8") as f:
    mm_dict = json.load(f)

# 🌐 Flask for Render
app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot is running ✔"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

# user mode
user_mode = {}

# 📚 dictionary API
def get_word_data(word):
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        res = requests.get(url, timeout=5)

        if res.status_code != 200:
            return None

        data = res.json()[0]

        result = f"📖 Word: {word}\n\n"

        # 🇲🇲 Myanmar
        if word in mm_dict:
            result += f"🇲🇲 Myanmar: {mm_dict[word]}\n\n"

        # pronunciation
        if "phonetic" in data:
            result += f"🔊 Pronunciation: {data['phonetic']}\n\n"

        # meanings
        for m in data["meanings"]:
            result += f"🔹 {m['partOfSpeech']}\n"
            for d in m["definitions"][:2]:
                result += f"- {d['definition']}\n"
            result += "\n"

        # synonyms
        synonyms = []
        for m in data["meanings"]:
            if "synonyms" in m:
                synonyms += m["synonyms"]

        if synonyms:
            result += "🔁 Synonyms: " + ", ".join(synonyms[:5]) + "\n\n"

        return result

    except Exception as e:
        print("Error:", e)
        return None

# 🧠 AI explanation (free logic)
def ai_explain(word):
    text = f"🧠 Explanation for '{word}':\n"

    if word in mm_dict:
        text += f"🇲🇲 Meaning: {mm_dict[word]}\n"

    text += "🔹 Type: common English word\n"
    text += "🔹 Usage: used in daily conversation\n"
    text += "🔹 Tip: try using it in your own sentence\n"

    return text

# 📌 Example sentence
def example_sentence(word):
    return f"📌 Example:\nI use the word '{word}' in a sentence."

# 🔊 voice
def make_voice(text):
    try:
        tts = gTTS(text=text, lang="en")
        file = "voice.mp3"
        tts.save(file)
        return file
    except:
        return None

# 🔎 Word suggestion
def suggest_words(prefix):
    suggestions = [w for w in mm_dict.keys() if w.startswith(prefix)]
    return suggestions[:5]

# 🌐 Myanmar translate improve
def translate_text(text):
    word = text.lower()

    if word in mm_dict:
        return f"🇲🇲 Myanmar: {mm_dict[word]}"

    return "❌ Myanmar meaning မရှိသေးဘူး (Dictionary mode သုံးပါ)"

# 🚀 start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📖 Dictionary", "🌐 Translate"]]
    await update.message.reply_text(
        "👋 Welcome!",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# 💬 handler
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()
    user_id = update.effective_user.id

    # mode switch
    if text == "📖 dictionary":
        user_mode[user_id] = "dict"
        await update.message.reply_text("📖 Dictionary mode")
        return

    if text == "🌐 translate":
        user_mode[user_id] = "trans"
        await update.message.reply_text("🌐 Translate mode")
        return

    mode = user_mode.get(user_id, "dict")

    # 🔎 suggestion first
    suggestions = suggest_words(text)
    if suggestions:
        await update.message.reply_text("💡 Suggestions:\n" + ", ".join(suggestions))

    if mode == "dict":
        data = get_word_data(text)

        if data:
            await update.message.reply_text(data)

            # example
            await update.message.reply_text(example_sentence(text))

            # AI explain
            await update.message.reply_text(ai_explain(text))

            # voice
            voice = make_voice(text)
            if voice:
                await update.message.reply_voice(voice=open(voice, "rb"))
                os.remove(voice)

        else:
            await update.message.reply_text("❌ Not found")

    else:
        result = translate_text(text)
        await update.message.reply_text(result)

# ⚠️ error handler
async def error_handler(update, context):
    print("Error:", context.error)

# 🌐 run
if __name__ == "__main__":
    threading.Thread(target=run_web).start()

    app = ApplicationBuilder().token("8618858114:AAE9oPIuTl_tH5FWVEwlwgkOw8APBsFjeg8").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle))
    app.add_error_handler(error_handler)

    print("Bot running...")
    app.run_polling()
