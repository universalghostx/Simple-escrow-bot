import os
import json
import logging
from telebot import TeleBot, types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config.json if present
CONFIG_FILE = "config.json"
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE) as f:
        config = json.load(f)
else:
    config = {}

TOKEN = config.get("token", os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_TOKEN_HERE"))
WALLET = config.get("wallet", os.environ.get("WALLET", "YOUR_WALLET_HERE"))

if not TOKEN or not WALLET:
    logger.error("Please set token and wallet in config.json or environment variables.")
    exit(1)

bot = TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message: types.Message):
    bot.reply_to(message, f"Hello {message.from_user.first_name}! Wallet: {WALLET}")

@bot.message_handler(commands=['wallet'])
def show_wallet(message: types.Message):
    bot.reply_to(message, f"Your wallet: {WALLET}")

@bot.message_handler(func=lambda m: True)
def echo(message: types.Message):
    bot.reply_to(message, f"You said: {message.text}")

if __name__ == "__main__":
    logger.info("Bot starting...")
    bot.infinity_polling()