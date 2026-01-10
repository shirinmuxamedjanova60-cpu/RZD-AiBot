import telebot
import requests
import json
import os
from flask import Flask
from threading import Thread

# --- НАСТРОЙКИ ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OPENROUTER_KEY = os.environ.get('OPENROUTER_KEY')
MODEL_NAME = "mistralai/mistral-7b-instruct:free"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Бот работает!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

@bot.message_handler(func=lambda message: True)
def handle_ai_request(message):
    print(f"--- Новое сообщение: {message.text} ---")
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
            error_text = result.get('error', {}).get('message', 'Ошибка API')
            bot.reply_to(message, f"ИИ недоступен: {error_text}")
            
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.reply_to(message, f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    # Запуск веб-сервера
    server_thread = Thread(target=run_web)
    server_thread.daemon = True
    server_thread.start()
    
    print("Бот запущен!")
    # infinity_polling решит проблему 409 Conflict при перезагрузке
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
