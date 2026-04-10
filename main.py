import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from playwright.async_api import async_playwright

# ====== CONFIG ======
BOT_TOKEN = "8622345566:AAEupxcluy4LUC3DR2QPWE6wImDfFbuyxGo"
OWNER_ID = 123456789  # ← PUT YOUR TELEGRAM ID HERE

# ====== RATES ======
rates = {
    "br": 210,
    "php": 235
}

# ====== SECURITY ======
allowed_users = 5392090963

# ====== DATA ======
diamond_data = {
    11:   (["10+1 (PHP)"], 9.5, 0),
    22:   (["20+2 (PHP)"], 19.0, 0),
    33:   (["20+2 (PHP)", "10+1 (PHP)"], 28.5, 0),
    44:   (["20+2 (PHP)", "20+2 (PHP)"], 38.0, 0),
    56:   (["51+5 (PHP)"], 47.5, 0),
    112:  (["102+10 (PHP)"], 95.0, 0),
    223:  (["203+20 (PHP)"], 190.0, 0),
    336:  (["303+33 (PHP)"], 285.0, 0),
    570:  (["504+66 (PHP)"], 475.0, 0),
    1163: (["1007+156 (PHP)"], 950.0, 0),

    86:   (["78+8 (BR)"], 0, 61.5),
    172:  (["156+16 (BR)"], 0, 122.0),
    257:  (["234+23 (BR)"], 0, 177.5),
    514:  (["234+23 (BR)", "234+23 (BR)"], 0, 355.0),
    600:  (["234+23 (BR)", "234+23 (BR)", "78+8 (BR)"], 0, 416.5),
    706:  (["625+81 (BR)"], 0, 480.0),
    878:  (["625+81 (BR)", "156+16 (BR)"], 0, 602.0),
    963:  (["625+81 (BR)", "234+23 (BR)"], 0, 657.5),
    1049: (["625+81 (BR)", "234+23 (BR)", "78+8 (BR)"], 0, 719.0),
    1135: (["625+81 (BR)", "234+23 (BR)", "156+16 (BR)"], 0, 779.5),
    1220: (["625+81 (BR)", "234+23 (BR)", "234+23 (BR)"], 0, 835.0),
    1412: (["625+81 (BR)", "625+81 (BR)"], 0, 960.0),
    2195: (["1860+335 (BR)"], 0, 1453.0),
    3688: (["3099+589 (BR)"], 0, 2424.0),

    279:  (["234+23 (BR)", "20+2 (PHP)"], 19.0, 177.5),
    343:  (["234+23 (BR)", "78+8 (BR)"], 0, 239.0),
    429:  (["234+23 (BR)", "156+16 (BR)"], 0, 299.5),
    1249: (["1007+156 (PHP)", "78+8 (BR)"], 950.0, 61.5),
    1420: (["1007+156 (PHP)", "234+23 (BR)"], 950.0, 177.5),
}

dd_data = {
    50:  ("Double Diamond 50", 39.0),
    150: ("Double Diamond 150", 116.9),
    250: ("Double Diamond 250", 187.5),
    500: ("Double Diamond 500", 385.0),
}

special = {
    "wp": ("Weekly Pass", 76.0),
    "tp": ("Twilight Pass", 402.5),
    "wep": ("Weekly Elite Pack", 39.0),
    "mep": ("Monthly Epic Pack", 196.5),
}

# ====== UTILS ======
def mmk(x):
    return f"{int(x):,} Ks"

def calc_total(php, br):
    return php * rates["php"] + br * rates["br"]

# ====== START ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🤖 Bot Ready\n\nYour ID: {update.effective_user.id}"
    )

# ====== LIST ======
async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📦 PRODUCT LIST (MMK)\n\n💎 Diamonds\n"
    for k in sorted(diamond_data):
        php, br = diamond_data[k][1], diamond_data[k][2]
        msg += f"{k:<5} → {mmk(calc_total(php, br))}\n"

    msg += "\n🔷 Double Diamond\n"
    for k in dd_data:
        msg += f"DD{k:<4} → {mmk(dd_data[k][1] * rates['br'])}\n"

    msg += "\n🎫 Special\n"
    for k in special:
        msg += f"{k.upper():<5} → {mmk(special[k][1] * rates['br'])}\n"

    await update.message.reply_text(msg)

# ====== INPUT ======
async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if text.startswith("dd"):
        num = int(text.replace("dd", ""))
        if num in dd_data:
            name, cost = dd_data[num]
            await update.message.reply_text(
                f"🔷 {name}\n\n💰 Cost: {cost}\n💵 Final: {mmk(cost * rates['br'])}"
            )
        return

    if text in special:
        name, cost = special[text]
        await update.message.reply_text(
            f"🎁 {name}\n\n💰 Cost: {cost}\n💵 Final: {mmk(cost * rates['br'])}"
        )
        return

    if text.isdigit():
        num = int(text)
        if num in diamond_data:
            packs, php, br = diamond_data[num]
            combo = "\n".join([f"- {p}" for p in packs])
            total = calc_total(php, br)

            await update.message.reply_text(
                f"📦 {num} Diamonds\n\n🧩 Combo:\n{combo}\n\n💰 Cost:\nBR: {br}\nPHP: {php}\n\n💵 Final:\n{mmk(total)}"
            )

# ====== RATE ======
async def setbr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rates["br"] = float(context.args[0])
    await update.message.reply_text(f"✅ BR set to {rates['br']}")

async def setphp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rates["php"] = float(context.args[0])
    await update.message.reply_text(f"✅ PHP set to {rates['php']}")

# ====== RECHARGE ======
async def recharge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in allowed_users:
        await update.message.reply_text("❌ Not allowed")
        return

    uid, zone, product, qty = context.args

    await update.message.reply_text("⏳ Processing...")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            ctx = await browser.new_context(storage_state="state.json")
            page = await ctx.new_page()

            await page.goto("https://www.smile.one/merchant/mobilelegends")
            await page.wait_for_timeout(5000)

            await update.message.reply_text(
                f"✅ SUCCESS\n\nUID: {uid} ({zone})\nProduct: {product} x{qty}"
            )

            await browser.close()

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ====== RUN ======
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("list", list_cmd))
app.add_handler(CommandHandler("setbr", setbr))
app.add_handler(CommandHandler("setphp", setphp))
app.add_handler(CommandHandler("recharge", recharge))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))

print("Bot running...")
app.run_polling()
