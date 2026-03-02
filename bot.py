import requests
import sqlite3
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8598041576:AAGvH_jizzssSSB1folNLyLUqCe8AxqDRCw"
WALLET = "TRuHXCeJXJ9L8temLhLzdeXwruRuV3HHtR"
API_KEY = "85b61665-8690-466f-8128-60bd27e8d2e2"

# Database
conn = sqlite3.connect("escrow.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS escrows (
    id TEXT,
    buyer_id INTEGER,
    seller TEXT,
    amount REAL,
    paid INTEGER DEFAULT 0
)
""")
conn.commit()

def generate_id():
    import random
    return str(random.randint(10000, 99999))

async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        seller = context.args[0]
        amount = float(context.args[1])
    except:
        await update.message.reply_text("Usage: /create @seller amount")
        return

    escrow_id = generate_id()
    cursor.execute("INSERT INTO escrows VALUES (?, ?, ?, ?, 0)",
                   (escrow_id, update.effective_user.id, seller, amount))
    conn.commit()

    await update.message.reply_text(
        f"Escrow ID: {escrow_id}\n"
        f"Send EXACT {amount} USDT (TRC20) to:\n{WALLET}"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    escrow_id = context.args[0]
    cursor.execute("SELECT * FROM escrows WHERE id=?", (escrow_id,))
    escrow = cursor.fetchone()

    if escrow:
        paid = "YES" if escrow[4] else "NO"
        await update.message.reply_text(
            f"Escrow {escrow_id}\nPaid: {paid}"
        )
    else:
        await update.message.reply_text("Escrow not found.")

async def check_payments(app):
    while True:
        url = f"https://api.trongrid.io/v1/accounts/{WALLET}/transactions/trc20"
        headers = {"TRON-PRO-API-KEY": API_KEY}
        r = requests.get(url, headers=headers)
        data = r.json()

        for tx in data.get("data", []):
            amount = int(tx["value"]) / 1_000_000
            cursor.execute("SELECT id FROM escrows WHERE amount=? AND paid=0", (amount,))
            escrow = cursor.fetchone()

            if escrow:
                cursor.execute("UPDATE escrows SET paid=1 WHERE id=?", (escrow[0],))
                conn.commit()

        await asyncio.sleep(30)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Simple Escrow Bot Ready.")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("create", create))
app.add_handler(CommandHandler("status", status))

app.job_queue.run_once(lambda ctx: asyncio.create_task(check_payments(app)), 1)

app.run_polling()
