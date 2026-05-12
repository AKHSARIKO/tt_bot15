import telebot
import requests
from telebot import types

# ЗАМЕНИ НА СВОЙ ТОКЕН
TOKEN = '8581710745:AAGnjA1dkEEkUmVgyRCGTNBfLMpX80MhIl4'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 
        "Привет! 👋 Я скачаю любое видео из TikTok без водяного знака.\n\n"
        "📥 Просто пришли мне ссылку на ролик!")

@bot.message_handler(func=lambda m: 'tiktok.com' in m.text)
def download_tt(message):
    msg = bot.send_message(message.chat.id, "⏳ Начинаю загрузку видео в чат...")
    try:
        res = requests.get(f"https://tikwm.com{message.text}").json()
        video_url = res['data']['play']
        bot.send_video(message.chat.id, video_url, caption="✅ Готово!")
        bot.delete_message(message.chat.id, msg.message_id)
    except:
        bot.edit_message_text("❌ Ошибка! Проверь ссылку.", message.chat.id, msg.message_id)

bot.polling(none_stop=True)
