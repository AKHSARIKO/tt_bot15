import telebot
import requests
import re

TOKEN = '8581710745:AAHdq0waBFf8jUQWdw_wYQFSZlj04LItBA8' # Проверь, что тут твой актуальный токен!
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 
        "Привет! 👋 Я пришлю видео из TikTok прямо сюда без водяного знака.\n\n"
        "📥 Просто отправь мне ссылку!")

@bot.message_handler(func=lambda m: 'tiktok.com' in m.text)
def download_tt(message):
    msg = bot.send_message(message.chat.id, "⏳ Обрабатываю видео, подожди немного...")
    try:
        # Извлекаем чистую ссылку
        link = re.findall(r'https?://[^\s]+', message.text)[0]
        
        # Запрос к более стабильному API
        options = {
            "url": link,
            "hd": 1
        }
        res = requests.post("https://tikwm.com", data=options).json()
        
        video_url = "https://tikwm.com" + res['data']['play']
        
        bot.send_video(message.chat.id, video_url, caption="✅ Готово! @ВашНик")
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Не удалось скачать. Попробуй другую ссылку или чуть позже.", message.chat.id, msg.message_id)

bot.polling(none_stop=True)
