# -*- coding: utf-8 -*-

import asyncio
import subprocess
import os
from datetime import datetime

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from playwright.async_api import async_playwright

# =========================
# 🔧 INSTALL PLAYWRIGHT
# =========================
subprocess.run(["playwright", "install", "chromium"])

# =========================
# 🔑 CONFIG
# =========================
BOT_TOKEN = "8622345566:AAH1Uj7Hcl2bvHZ4AoOblRaY7qy_NbYUguA"
OWNER_ID = 5392090963

rates = {
    "br": 83,
    "php": 73
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
    await update.message.reply_text(f"🤖 Bot Ready\n🆔 {update.effective_user.id}")

# =========================
# 📦 LIST
# =========================
async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📦 PRODUCT LIST\n\n"

    for k, v in sorted(diamond_data.items()):
        php, br = v[1], v[2]
        total = calc_total(php, br)
        msg += f"{str(k).ljust(5)} → {mmk(total)}\n"

    msg += "\n🎫 PASSES\n"
    msg += "wp   → Weekly Pass\n"
    msg += "tp   → Twilight Pass\n"
    msg += "wep  → Weekly Elite Bundle\n"
    msg += "mep  → Monthly Epic Bundle\n"

    await update.message.reply_text(msg)

# =========================
# 💬 MESSAGE HANDLER
# =========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if text.isdigit():
        num = int(text)
        if num in diamond_data:
            packs, php, br = diamond_data[num]
            total = calc_total(php, br)

            msg = f"💎 {num}\n\n"
            for p in packs:
                msg += f"• {p}\n"

            msg += f"\n💰 BR: {br}\nPHP: {php}\n"
            msg += f"\n💵 {mmk(total)}"

            await update.message.reply_text(msg)

    elif text in special_products:
        name, php, br = special_products[text]
        total = calc_total(php, br)

        msg = f"🎫 {text.upper()}\n\n"
        msg += f"• {name[0]}\n"
        msg += f"\n💰 BR: {br}\nPHP: {php}\n"
        msg += f"\n💵 {mmk(total)}"

        await update.message.reply_text(msg)

# =========================
# ⚙️ RECHARGE (DEBUG)
# =========================
async def recharge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ Not allowed")
        return

    try:
        uid, zone, product, qty = context.args
        product = int(product)
    except:
        await update.message.reply_text("❌ Usage:\n/recharge UID ZONE PRODUCT QTY")
        return

    await update.message.reply_text("🔄 Step 1: Starting...")

    try:
        async with async_playwright() as p:
            await update.message.reply_text("🔄 Step 2: Launch browser...")

            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
            )

            page = await browser.new_page()

            await update.message.reply_text("🔄 Step 3: Open site...")
            await page.goto("https://www.smile.one", timeout=60000)

            await page.wait_for_timeout(5000)

            await update.message.reply_text("🔄 Step 4: Fill UID...")
            await page.get_by_placeholder("User ID").fill(uid)
            await page.get_by_placeholder("Zone ID").fill(zone)

            await asyncio.sleep(3)

            packs, php, br = diamond_data[product]

            await update.message.reply_text("🔄 Step 5: Select packs...")

            for p_name in packs:
                try:
                    text = p_name.split(" ")[0]
                    await page.get_by_text(text).first.click(timeout=5000)
                    await asyncio.sleep(1.5)
                except:
                    await update.message.reply_text(f"⚠️ Pack not found: {p_name}")

            await update.message.reply_text("🔄 Step 6: Payment...")

            try:
                await page.get_by_text("SmileCoin").click(timeout=5000)
            except:
                await update.message.reply_text("⚠️ Payment not found")

            await asyncio.sleep(2)

            await update.message.reply_text("🔄 Step 7: Buy...")

            try:
                await page.get_by_text("Buy now").click(timeout=5000)
            except:
                await update.message.reply_text("⚠️ Buy button not found")

            await asyncio.sleep(5)

            total = calc_total(php, br)

            await update.message.reply_text(
                f"✅ SUCCESS\n\n"
                f"🆔 {uid} ({zone})\n"
                f"📦 {product}\n\n"
                f"💵 {mmk(total)}"
            )

            await browser.close()

    except Exception as e:
        await update.message.reply_text(f"❌ Error:\n{e}")

# =========================
# 🚀 RUN
# =========================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("list", list_cmd))
app.add_handler(CommandHandler("recharge", recharge))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()