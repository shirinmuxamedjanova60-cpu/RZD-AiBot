import telebot
import requests
import json
import os
from flask import Flask
from threading import Thread

# --- НАСТРОЙКИ ИЗ ENVIRONMENT VARIABLES (RENDER) ---
# Эти данные подтягиваются из раздела Advanced вашего проекта
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OPENROUTER_KEY = os.environ.get('OPENROUTER_KEY')
# Используем бесплатную и быструю модель
MODEL_NAME = "google/gemini-2.0-flash-lite-preview-02-05:free"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask('')

# --- ВЕБ-СЕРВЕР ДЛЯ ПОДДЕРЖАНИЯ ЖИЗНИ (RENDER + CRON-JOB) ---
@app.route('/')
def home():
    return "RZDBot is running!" # Ответ для Cron-job

def run_web():
    # Render использует порт 8080 по умолчанию
    app.run(host='0.0.0.0', port=8080)

# --- ОБРАБОТКА СООБЩЕНИЙ ---
@bot.message_handler(func=lambda message: True)
def handle_ai_request(message):
    try:
        # Отправляем запрос в OpenRouter
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": message.text}]
            }),
            timeout=30 # Тайм-аут, чтобы бот не зависал
        )
        
        result = response.json()
        
        # Проверяем, есть ли ответ в структуре JSON
        if 'choices' in result:
            ai_message = result['choices'][0]['message']['content']
            bot.reply_to(message, ai_message)
        else:
            print(f"Ошибка API: {result}")
            bot.reply_to(message, "ИИ временно недоступен. Попробуйте позже.")
            
    except Exception as e:
        print(f"Ошибка в handle_ai_request: {e}")

# --- ЗАПУСК ---
if __name__ == "__main__":
    # 1. Запускаем веб-сервер в фоновом потоке
    server_thread = Thread(target=run_web)
    server_thread.start()
    
    print("Бот запущен и готов к работе!")
    
    # 2. Запускаем бесконечный опрос Telegram (устойчив к ошибкам 409)
    try:
        bot.infinity_polling(timeout=20, long_polling_timeout=10)
    except Exception as e:
        print(f"Критическая ошибка polling: {e}")
