import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "YOUR_BOT_TOKEN_HERE"

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a word")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text.lower()
    data = get_word_data(word)

    if data:
        await update.message.reply_text(data)
    else:
        await update.message.reply_text("❌ Word not found")


app = ApplicationBuilder().token(8618858114:AAFPOPsD3otTIlcb35Yzv88cHsxUSXjw8UY).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot running...")
app.run_polling()
