# -*- coding: utf-8 -*-

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# =========================
# 🔑 CONFIG
# =========================
BOT_TOKEN = "8622345566:AAH1Uj7Hcl2bvHZ4AoOblRaY7qy_NbYUguA"
OWNER_ID = 5392090963

rates = {
    "br": 83.0,
    "php": 73.0
}

# =========================
# 💎 DIAMONDS
# =========================
diamond_data = {
    11: (["10+1 (PHP)"], 9.5, 0),
    22: (["20+2 (PHP)"], 19.0, 0),
    33: (["20+2 (PHP)", "10+1 (PHP)"], 28.5, 0),
    44: (["20+2 (PHP)", "20+2 (PHP)"], 38.0, 0),
    56: (["51+5 (PHP)"], 47.5, 0),

    86: (["78+8 (BR)"], 0, 61.5),
    112: (["102+10 (PHP)"], 95.0, 0),
    172: (["156+16 (BR)"], 0, 122.0),
    223: (["203+20 (PHP)"], 190.0, 0),
    257: (["234+23 (BR)"], 0, 177.5),

    279: (["234+23 (BR)", "20+2 (PHP)"], 19.0, 177.5),
    343: (["234+23 (BR)", "78+8 (BR)"], 0, 239.0),
    429: (["234+23 (BR)", "156+16 (BR)"], 0, 299.5),
    514: (["234+23 (BR)", "234+23 (BR)"], 0, 355.0),
    600: (["234+23 (BR)", "234+23 (BR)", "78+8 (BR)"], 0, 416.5),

    706: (["625+81 (BR)"], 0, 480.0),
    878: (["625+81 (BR)", "156+16 (BR)"], 0, 602.0),
    963: (["625+81 (BR)", "234+23 (BR)"], 0, 657.5),
    1049: (["625+81 (BR)", "234+23 (BR)", "78+8 (BR)"], 0, 719.0),
    1135: (["625+81 (BR)", "234+23 (BR)", "156+16 (BR)"], 0, 779.5),

    1220: (["625+81 (BR)", "234+23 (BR)", "234+23 (BR)"], 0, 835.0),
    1412: (["625+81 (BR)", "625+81 (BR)"], 0, 960.0),
    2195: (["1860+335 (BR)"], 0, 1453.0),
    3688: (["3099+589 (BR)"], 0, 2424.0),
}

# =========================
# 🎫 PASSES
# =========================
special_products = {
    "wp": (["Weekly Pass"], 0, 76),
    "tp": (["Twilight Pass"], 0, 320),
    "wep": (["Weekly Elite Bundle"], 0, 45),
    "mep": (["Monthly Epic Bundle"], 0, 225),
}

# =========================
# 🧮 HELPERS
# =========================
def calc_total(php, br):
    return php * rates["php"] + br * rates["br"]

def mmk(x):
    return f"{int(x):,} Ks"

# =========================
# ▶️ START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id == OWNER_ID:
        await update.message.reply_text(
            f"🤖 MLBB Recharge Bot (Admin)\n\n"
            f"🆔 {user_id}\n\n"
            f"━━━━━━━━━━━━━━\n"
            f"📦 /list → Prices\n"
            f"💱 /setbr 85\n"
            f"💱 /setphp 75\n\n"
            f"━━━━━━━━━━━━━━"
        )
    else:
        await update.message.reply_text(
            f"💎 MLBB Diamond Shop\n\n"
            f"━━━━━━━━━━━━━━\n"
            f"💎 Send amount → 279\n"
            f"🎫 Passes → wp / tp / wep / mep\n\n"
            f"📦 /list → View prices\n"
            f"━━━━━━━━━━━━━━"
        )

# =========================
# 📦 LIST
# =========================
async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📦 DIAMONDS\n\n"

    for k, v in sorted(diamond_data.items()):
        php, br = v[1], v[2]
        total = calc_total(php, br)
        msg += f"{str(k).ljust(5)} → {mmk(total)}\n"

    msg += "\n━━━━━━━━━━━━━━\n🎫 PASSES\n\n"

    for key, val in special_products.items():
        php, br = val[1], val[2]
        total = calc_total(php, br)
        msg += f"{key.ljust(5)} → {mmk(total)}\n"

    msg += "\n━━━━━━━━━━━━━━\n"
    msg += f"📊 Rates\nBR: {rates['br']} | PHP: {rates['php']}"

    await update.message.reply_text(msg)

# =========================
# 💱 SET RATES
# =========================
async def setbr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Not allowed")
        return
    try:
        rates["br"] = float(context.args[0])
        await update.message.reply_text(f"✅ BR rate updated → {rates['br']}")
    except:
        await update.message.reply_text("❌ Usage: /setbr 85")

async def setphp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Not allowed")
        return
    try:
        rates["php"] = float(context.args[0])
        await update.message.reply_text(f"✅ PHP rate updated → {rates['php']}")
    except:
        await update.message.reply_text("❌ Usage: /setphp 75")

# =========================
# 💬 MESSAGE HANDLER
# =========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    # 💎 Diamonds
    if text.isdigit():
        num = int(text)
        if num in diamond_data:
            packs, php, br = diamond_data[num]
            total = calc_total(php, br)

            msg = f"💎 {num} Diamonds\n\n📦 Packs:\n"
            for p in packs:
                msg += f"• {p}\n"

            msg += f"\n💰 Cost:\nBR: {br}\nPHP: {php}\n"
            msg += f"\n💵 Total: {mmk(total)}"

            await update.message.reply_text(msg)

    # 🎫 Passes
    elif text in special_products:
        name, php, br = special_products[text]
        total = calc_total(php, br)

        msg = f"🎫 {name[0]}\n\n"
        msg += f"💰 Cost:\nBR: {br}\nPHP: {php}\n"
        msg += f"\n💵 {mmk(total)}"

        await update.message.reply_text(msg)

# =========================
# 🚀 RUN
# =========================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("list", list_cmd))
app.add_handler(CommandHandler("setbr", setbr))
app.add_handler(CommandHandler("setphp", setphp))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()