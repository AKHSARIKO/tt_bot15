import telebot
import requests
import re
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telebot import types

TOKEN = os.environ.get('BOT_TOKEN', '8581710745:AAFq3pYlHowkbgRV-JiVD0r0t_Zap3dLTL8')
bot = telebot.TeleBot(TOKEN)



CHANNEL_USERNAME = "@my_tiktok_bot_news"

# === ВЕБ-СЕРВЕР ДЛЯ ОБХОДА ТАРИФА RENDER ===
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()
print("--- ВЕБ-СЕРВЕР ЗАПУЩЕН ---")
# =============================================

def get_welcome_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_link = types.InlineKeyboardButton(text="📢 Подписаться на канал", url="/t.me/my_tiktok_bot_news")
    btn_check = types.InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")
    btn_promo = types.InlineKeyboardButton(text="📦 Реклама", url="@AKHSARIKO") 
    markup.add(btn_link, btn_check, btn_promo)
    return markup

# ПРИОРИТЕТНЫЙ ОБРАБОТЧИК СТАРТА
@bot.message_handler(commands=['start'])
def start(message):
    print(f"--> Получена команда /start от пользователя {message.from_user.id}")
    welcome_text = "Привет! 👋 Чтобы получить доступ к функциям бота, подпишитесь на мой канал и затем нажмите кнопку «✅ Я подписался»."
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_welcome_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_user_sub(call):
    user_id = call.from_user.id
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            bot.answer_callback_query(call.id, "Спасибо за подписку!")
            bot.send_message(call.message.chat.id, "🎉 Доступ открыт! Просто пришлите мне ссылку на ролик TikTok.")
        else:
            bot.answer_callback_query(call.id, "❌ Вы всё еще не подписались на канал!", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(call.id, "⚠️ Ошибка проверки. Убедитесь, что бот назначен администратором канала.", show_alert=True)

# ОБРАБОТЧИК ССЫЛОК TIKTOK
@bot.message_handler(func=lambda m: m.text and ('tiktok.com' in m.text or 'vt.tiktok' in m.text))
def download_tt(message):
    print(f"--> Получена ссылка на TikTok от пользователя {message.from_user.id}")
    user_id = message.from_user.id
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status not in ['member', 'administrator', 'creator']:
            bot.send_message(message.chat.id, "⚠️ Сначала необходимо подписаться на канал!", reply_markup=get_welcome_keyboard())
            return
    except:
        pass

    msg = bot.send_message(message.chat.id, "⏳ Скачиваю видео, подождите...")
    try:
        found_links = re.findall(r'https?://[^\s]+', message.text)
        if not found_links:
            bot.edit_message_text("❌ Ссылка на TikTok не найдена в сообщении.", message.chat.id, msg.message_id)
            return
            
        tiktok_url = found_links[0]
        options = {"url": tiktok_url, "hd": 1}
        
        res = requests.post("tikwm.com", data=options).json()
        
        if res.get('code') == 0:
            video_url = "https://tikwm.com" + res['data']['play']
            bot.send_video(message.chat.id, video_url)
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("❌ Не удалось скачать видео. Возможно, оно приватное.", message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка при обработке ссылки: {str(e)}", message.chat.id, msg.message_id)

print("--- БОТ ЗАПУЩЕН И ПОДКЛЮЧЕН К TELEGRAM ---")
bot.polling(none_stop=True)
