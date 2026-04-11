# -*- coding: utf-8 -*-

import asyncio
import subprocess
import os
from datetime import datetime

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from playwright.async_api import async_playwright

# =========================
# 🔧 FORCE INSTALL PLAYWRIGHT (RAILWAY FIX)
# =========================
if not os.path.exists("/root/.cache/ms-playwright"):
    subprocess.run(["playwright", "install", "chromium"])

# =========================
# 🔑 CONFIG (CHANGE ONLY THIS)
# =========================
BOT_TOKEN = "8622345566:AAEupxcluy4LUC3DR2QPWE6wImDfFbuyxGo"
OWNER_ID = 5392090963  # replace with your real Telegram ID

rates = {
    "br": 83,
    "php": 73
}

# =========================
# 💎 FULL DATA (NO MISSING)
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
    await update.message.reply_text(
        f"🤖 Bot Ready\n🆔 {update.effective_user.id}"
    )

# =========================
# 📦 LIST
# =========================
async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📦 PRODUCT LIST\n\n"

    for k, v in sorted(diamond_data.items()):
        php, br = v[1], v[2]
        total = calc_total(php, br)
        msg += f"{str(k).ljust(5)} → {mmk(total)}\n"

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

            msg = f"📦 {num}\n\n"
            for p in packs:
                msg += f"• {p}\n"

            msg += f"\n💰 BR: {br}\nPHP: {php}\nTOTAL: {php+br}\n"
            msg += f"\n💵 {mmk(total)}"

            await update.message.reply_text(msg)

# =========================
# ⚙️ RECHARGE
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

    await update.message.reply_text("🔄 Processing...")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu"
                ]
            )

            page = await browser.new_page()

            await page.goto("https://www.smile.one")
            await page.wait_for_load_state("networkidle")

            # Fill ID
            await page.get_by_placeholder("User ID").fill(uid)
            await page.get_by_placeholder("Zone ID").fill(zone)

            await page.mouse.click(100, 100)
            await asyncio.sleep(3)

            packs, php, br = diamond_data[product]

            for p_name in packs:
                text = p_name.split(" ")[0]
                await page.get_by_text(text).first.click()
                await asyncio.sleep(1)

            await page.get_by_text("SmileCoin").click()
            await asyncio.sleep(1)

            await page.get_by_text("Buy now").click()
            await asyncio.sleep(5)

            total = calc_total(php, br)

            await update.message.reply_text(
                f"✅ SUCCESS\n\n"
                f"🆔 {uid} ({zone})\n"
                f"📦 {product}\n\n"
                f"💰 BR:{br} PHP:{php} TOTAL:{php+br}\n"
                f"💵 {mmk(total)}\n"
                f"🕒 {datetime.now().strftime('%H:%M')}"
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
