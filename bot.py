import time
import json
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler, ContextTypes

logging.basicConfig(level=logging.ERROR)

TOKEN = "8622345566:AAEupxcluy4LUC3DR2QPWE6wImDfFbuyxGo"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔐 ACCESS CONTROL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ADMIN_ID = 5392090963
USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def is_allowed(user_id: int) -> bool:
    if user_id == ADMIN_ID:
        return True
    users = load_users()
    return str(user_id) in users

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💰 RATES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
rate_php = 84.5
rate_br = 84.5

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💎 DIAMOND DATA
# total_diamonds → (combo_labels, php_coins, br_coins)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
data = {
    # PHP only
    11:   (["10+1 (PHP)"],                                          9.5,     0),
    22:   (["20+2 (PHP)"],                                         19.0,     0),
    33:   (["20+2 (PHP)", "10+1 (PHP)"],                           28.5,     0),
    44:   (["20+2 (PHP)", "20+2 (PHP)"],                           38.0,     0),
    56:   (["51+5 (PHP)"],                                         47.5,     0),
    112:  (["102+10 (PHP)"],                                       95.0,     0),
    223:  (["203+20 (PHP)"],                                      190.0,     0),
    336:  (["303+33 (PHP)"],                                      285.0,     0),
    570:  (["504+66 (PHP)"],                                      475.0,     0),
    1163: (["1007+156 (PHP)"],                                    950.0,     0),

    # BR only
    86:   (["78+8 (BR)"],                                            0,   61.5),
    172:  (["156+16 (BR)"],                                          0,  122.0),
    257:  (["234+23 (BR)"],                                          0,  177.5),
    514:  (["234+23 (BR)", "234+23 (BR)"],                          0,  355.0),
    600:  (["234+23 (BR)", "234+23 (BR)", "78+8 (BR)"],             0,  416.5),
    706:  (["625+81 (BR)"],                                          0,  480.0),
    878:  (["625+81 (BR)", "156+16 (BR)"],                          0,  602.0),
    963:  (["625+81 (BR)", "234+23 (BR)"],                          0,  657.5),
    1049: (["625+81 (BR)", "234+23 (BR)", "78+8 (BR)"],             0,  719.0),
    1135: (["625+81 (BR)", "234+23 (BR)", "156+16 (BR)"],           0,  779.5),
    1220: (["625+81 (BR)", "234+23 (BR)", "234+23 (BR)"],           0,  835.0),
    1412: (["625+81 (BR)", "625+81 (BR)"],                          0,  960.0),
    2195: (["1860+335 (BR)"],                                        0, 1453.0),
    3688: (["3099+589 (BR)"],                                        0, 2424.0),

    # Mixed (BR primary, PHP fills gap)
    279:  (["234+23 (BR)", "20+2 (PHP)"],                          19.0, 177.5),
    343:  (["234+23 (BR)", "78+8 (BR)"],                            0.0, 239.0),
    429:  (["234+23 (BR)", "156+16 (BR)"],                          0.0, 299.5),
    1249: (["1007+156 (PHP)", "78+8 (BR)"],                       950.0,  61.5),
    1420: (["1007+156 (PHP)", "234+23 (BR)"],                     950.0, 177.5),
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔷 DOUBLE DIAMOND (all BR)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
dd_data = {
    50:  ("Double Diamond 50",  39.0),
    150: ("Double Diamond 150", 116.9),
    250: ("Double Diamond 250", 187.5),
    500: ("Double Diamond 500", 385.0),
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎫 SPECIAL ITEMS (all BR)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
special_items = {
    "wp": ("Weekly Pass",     76.0),
    "tp": ("Twinlight Pass", 402.5),
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔐 ADMIN: ALLOW / REVOKE / USERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def allow_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        target_id = str(int(context.args[0]))
        name = " ".join(context.args[1:]) if len(context.args) > 1 else "Unknown"
        users = load_users()
        users[target_id] = {
            "name": name,
            "granted": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_users(users)
        await update.message.reply_text(f"✅ Access granted to {name} (ID: {target_id})")
    except:
        await update.message.reply_text("Use: /allow <user_id> <name>")

async def revoke_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        target_id = str(int(context.args[0]))
        users = load_users()
        if target_id in users:
            name = users[target_id].get("name", target_id)
            del users[target_id]
            save_users(users)
            await update.message.reply_text(f"🚫 Access revoked from {name} (ID: {target_id})")
        else:
            await update.message.reply_text("❌ User not found in access list")
    except:
        await update.message.reply_text("Use: /revoke <user_id>")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    users = load_users()
    if not users:
        await update.message.reply_text("No approved users yet.")
        return
    lines = ["👥 Approved Users\n"]
    for uid, info in users.items():
        lines.append(f"• {info.get('name', 'Unknown')} (ID: {uid})\n  Granted: {info.get('granted', '—')}")
    await update.message.reply_text("\n".join(lines))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💎 HANDLE ALL MESSAGES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return

    global rate_php, rate_br
    text = update.message.text.strip().lower()

    # 🎫 Special items: wp / tp
    if text in special_items:
        label, br_coins = special_items[text]
        total = int(br_coins * rate_br)
        await update.message.reply_text(f"🎫 {label}\n\n💰 {total} MMK")
        return

    # 🔷 Double Diamond: "dd 250" or "dd250"
    if text.startswith("dd"):
        num_part = text[2:].strip()
        try:
            amount = int(num_part)
            if amount in dd_data:
                label, br_coins = dd_data[amount]
                total = int(br_coins * rate_br)
                await update.message.reply_text(f"🔷 {label}\n\n💰 {total} MMK")
            else:
                await update.message.reply_text("❌ DD not available\nOptions: dd 50 | dd 150 | dd 250 | dd 500")
        except:
            await update.message.reply_text("❌ DD not available\nOptions: dd 50 | dd 150 | dd 250 | dd 500")
        return

    # 💎 Regular diamonds
    try:
        target = int(text)
        if target in data:
            combo, php_coins, br_coins = data[target]
            total = int(php_coins * rate_php + br_coins * rate_br)
            combo_text = " + ".join(combo)
            await update.message.reply_text(f"💎 {target}\n\n{combo_text}\n\n💰 {total} MMK")
        else:
            await update.message.reply_text("❌ Not available\nSend /list to see all items")
    except:
        await update.message.reply_text(
            "Send diamond amount like: 279\n"
            "Double Diamond: dd 250\n"
            "Weekly Pass: wp\n"
            "Twinlight Pass: tp"
        )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💰 SET RATE (admin only)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def set_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return
    global rate_php, rate_br
    try:
        kind = context.args[0].lower()
        value = float(context.args[1])
        if kind == "php":
            rate_php = value
            await update.message.reply_text(f"✅ PHP Rate = {rate_php}")
        elif kind == "br":
            rate_br = value
            await update.message.reply_text(f"✅ BR Rate = {rate_br}")
        else:
            await update.message.reply_text("Use: /set php 84.5  or  /set br 85.0")
    except:
        await update.message.reply_text("Use: /set php 84.5  or  /set br 85.0")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋 LIST (allowed users)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def list_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return
    global rate_php, rate_br

    lines = ["📋 Price List\n"]

    lines.append("💎 Diamonds")
    for diamonds in sorted(data.keys()):
        combo, php_coins, br_coins = data[diamonds]
        total = int(php_coins * rate_php + br_coins * rate_br)
        lines.append(f"  {diamonds} → {total} MMK")

    lines.append("\n🔷 Double Diamond")
    for amount in sorted(dd_data.keys()):
        label, br_coins = dd_data[amount]
        total = int(br_coins * rate_br)
        lines.append(f"  DD {amount} → {total} MMK")

    lines.append("\n🎫 Special Items")
    for key, (label, br_coins) in special_items.items():
        total = int(br_coins * rate_br)
        lines.append(f"  {label} ({key}) → {total} MMK")

    await update.message.reply_text("\n".join(lines))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 START
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id):
        return
    await update.message.reply_text(
        "💎 Diamonds — send the amount (e.g. 279)\n"
        "🔷 Double Diamond — send dd + amount (e.g. dd 250)\n"
        "🎫 Weekly Pass — send: wp\n"
        "🎫 Twinlight Pass — send: tp\n\n"
        "/list — see all prices\n"
        "/set php 84.5 — update PHP rate\n"
        "/set br 85.0 — update BR rate"
    )

def build_app():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("set", set_rate))
    app.add_handler(CommandHandler("list", list_items))
    app.add_handler(CommandHandler("allow", allow_user))
    app.add_handler(CommandHandler("revoke", revoke_user))
    app.add_handler(CommandHandler("users", list_users))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    return app

while True:
    try:
        app = build_app()
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        print(f"Bot crashed: {e} — restarting in 5 seconds...")
        time.sleep(5)
