import os
import threading
from flask import Flask
import telebot

# --- 1. Настройка веб-сервера для Render ---
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running"

@app.route('/health')
def health():
    return "OK"

def run_web_server():
    # Render сам передаст нужный порт через переменную окружения PORT
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# --- 2. Твой код бота (немного изменённый) ---
TOKEN = os.environ.get('TELEGRAM_TOKEN') # Токен берётся из настроек Render
if not TOKEN:
    raise ValueError("Не найден TELEGRAM_TOKEN в переменных окружения!")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я помогу распределить карманные деньги по правилу 50/30/20.\n\n"
        "Напиши, сколько рублей ты получил? (только число)"
    )

@bot.message_handler(content_types=['text'])
def calculate_budget(message):
    text = message.text.replace(',', '.')
    try:
        summa = float(text)
        if summa <= 0:
            bot.send_message(message.chat.id, "Сумма должна быть больше нуля. Попробуй ещё раз.")
            return
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, напиши число. Например: 500")
        return

    need = int(summa * 0.5)
    want = int(summa * 0.3)
    save = int(summa * 0.2)

    reply = (
        f"Вот твой план на {int(summa)} руб.:\n\n"
        f"📌 На обязательные траты (50%): {need} руб.\n"
        f"🎮 На развлечения (30%): {want} руб.\n"
        f"💰 В копилку (20%): {save} руб.\n\n"
        f"Попробуй следовать этому плану неделю!"
    )
    bot.send_message(message.chat.id, reply)

# --- 3. Запуск ---
if __name__ == '__main__':
    # Запускаем веб-сервер в фоне (чтобы Render видел порт)
    web_thread = threading.Thread(target=run_web_server)
    web_thread.start()
    
    # Запускаем самого бота
    print("Бот запущен...")
    bot.polling(none_stop=True)