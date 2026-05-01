import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# user mode memory
user_mode = {}

# detect language (simple)
def detect_lang(text):
    mm_chars = "ကခဂဃငစဆဇဈဉညတထဒဓနပဖဗဘမယရလဝသဟအ"
    for c in text:
        if c in mm_chars:
            return "my"
    return "en"

# translate function
def translate(text, source, target):
    url = f"https://api.mymemory.translated.net/get?q={text}&langpair={source}|{target}"
    res = requests.get(url)
    data = res.json()
    return data["responseData"]["translatedText"]

# start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🌐 Auto Mode", callback_data="auto"),
            InlineKeyboardButton("🇲🇲 → 🇬🇧", callback_data="my-en"),
            InlineKeyboardButton("🇬🇧 → 🇲🇲", callback_data="en-my"),
        ]
    ]

    await update.message.reply_text(
        "👋 Amelia Free Translate Bot\nChoose mode:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# button click
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_mode[query.from_user.id] = query.data
    await query.edit_message_text(f"✅ Mode set: {query.data}")

# message handler
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    mode = user_mode.get(user_id, "auto")

    try:
        if mode == "auto":
            src = detect_lang(text)
            target = "en" if src == "my" else "my"

        elif mode == "my-en":
            src, target = "my", "en"

        else:
            src, target = "en", "my"

        result = translate(text, src, target)

        await update.message.reply_text(f"🌍 {src} → {target}\n{result}")

    except Exception as e:
        await update.message.reply_text("❌ Error: " + str(e))


app = ApplicationBuilder().token("8618858114:AAFPOPsD3otTIlcb35Yzv88cHsxUSXjw8UY").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("FREE PRO BOT RUNNING...")
app.run_polling()