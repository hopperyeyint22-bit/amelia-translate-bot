import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "YOUR_BOT_TOKEN_HERE"

# user mode storage
user_mode = {}

# 📚 Dictionary function
def get_word_data(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    res = requests.get(url)

    if res.status_code != 200:
        return None

    data = res.json()[0]
    meanings = data["meanings"]

    result = f"📖 Word: {word}\n\n"

    if "phonetic" in data:
        result += f"🔊 Pronunciation: {data['phonetic']}\n\n"

    for meaning in meanings:
        part = meaning["partOfSpeech"]
        result += f"🔹 {part}\n"

        for i, d in enumerate(meaning["definitions"][:2]):
            result += f"{i+1}. {d['definition']}\n"

            if "example" in d:
                result += f"   📌 {d['example']}\n"

        result += "\n"

    return result


# 🌐 Simple Translate (FREE)
def translate_text(text):
    url = "https://api.mymemory.translated.net/get"
    res = requests.get(url, params={"q": text, "langpair": "en|my"})

    if res.status_code != 200:
        return "❌ Translate error"

    return res.json()["responseData"]["translatedText"]


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📖 Dictionary", "🌐 Translate"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    user_mode[update.effective_user.id] = "dictionary"

    await update.message.reply_text(
        "👋 Choose mode:",
        reply_markup=reply_markup
    )


# handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # switch mode
    if text == "📖 Dictionary":
        user_mode[user_id] = "dictionary"
        await update.message.reply_text("📖 Dictionary mode activated")
        return

    elif text == "🌐 Translate":
        user_mode[user_id] = "translate"
        await update.message.reply_text("🌐 Translate mode activated")
        return

    # check mode
    mode = user_mode.get(user_id, "dictionary")

    if mode == "dictionary":
        data = get_word_data(text.lower())
        if data:
            await update.message.reply_text(data)
        else:
            await update.message.reply_text("❌ Word not found")

    elif mode == "translate":
        result = translate_text(text)
        await update.message.reply_text(f"🌐 {result}")


# main
app = ApplicationBuilder().token("8618858114:AAG1MJQxqPdxjgCN3NRENWTKEbbPGf1o5m4").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot running...")
app.run_polling()
