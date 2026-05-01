import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "YOUR_BOT_TOKEN_HERE"

# 📚 Dictionary function
def get_word_data(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    res = requests.get(url)

    if res.status_code != 200:
        return None

    data = res.json()[0]

    meaning_list = data["meanings"]

    result = f"📖 Word: {word}\n\n"

    # pronunciation
    try:
        result += f"🔊 Pronunciation: {data['phonetic']}\n\n"
    except:
        pass

    for meaning in meaning_list:
        part = meaning["partOfSpeech"]
        result += f"🔹 Part of speech: {part}\n"

        for i, defn in enumerate(meaning["definitions"][:2]):
            result += f"{i+1}. {defn['definition']}\n"

            if "example" in defn:
                result += f"   📌 Example: {defn['example']}\n"

        result += "\n"

    return result


# 📩 message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text.lower()

    data = get_word_data(word)

    if data:
        await update.message.reply_text(data)
    else:
        await update.message.reply_text("❌ Word not found")


# start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a word to get dictionary meaning!")


# main
app = ApplicationBuilder().token(8618858114:AAFPOPsD3otTIlcb35Yzv88cHsxUSXjw8UY).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot is running...")
app.run_polling()
