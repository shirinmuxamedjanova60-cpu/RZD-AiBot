import telebot
import requests
import json
import os
from flask import Flask
from threading import Thread

# --- НАСТРОЙКИ (Данные из Render Environment Variables) ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OPENROUTER_KEY = os.environ.get('OPENROUTER_KEY')

# ЗАМЕНЕНО: Поставил самую надежную бесплатную модель Mistral
MODEL_NAME = "mistralai/mistral-7b-instruct:free"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask('')

# --- ВЕБ-СЕРВЕР ДЛЯ ПОДДЕРЖАНИЯ ЖИЗНИ ---
@app.route('/')
def home():
    return "Бот активен!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

# --- ОБРАБОТКА СООБЩЕНИЙ ---
@bot.message_handler(func=lambda message: True)
def handle_ai_request(message):
    print(f"--- Получено: {message.text} ---")
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://render.com",
                "X-Title": "RZDBot"
            },
            data=json.dumps({
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": message.text}]
            }),
            timeout=30
        )
        
        result = response.json()
        print(f"Статус: {response.status_code}, Ответ: {result}")
        
        if 'choices' in result and len(result['choices']) > 0:
            ai_message = result['choices'][0]['message']['content']
            bot.reply_to(message, ai_message)
        else:
            # Бот теперь напишет в чат точную техническую ошибку
            error_text = result.get('error', {}).get('message', 'Неизвестная ошибка')
            bot.reply_to(message, f"Ошибка от ИИ: {error_text}")
            print(f"Ошибка API: {result}")
            
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.reply_to(message, f"Техническая ошибка: {str(e)}")

# --- ЗАПУСК ---
if __name__ == "__main__":
    server_thread = Thread(target=run_web)
    server_thread.daemon = True
    server_thread.start()
    
    print("Бот успешно запущен!")
    # infinity_polling защищает от вылетов при перезагрузке
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
