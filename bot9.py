import telebot
import requests
import json
import os
from flask import Flask
from threading import Thread

# Берем ключи из настроек Render (Advanced)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OPENROUTER_KEY = os.environ.get('OPENROUTER_KEY')
# Выбираем рабочую бесплатную модель
MODEL_NAME = "google/gemini-2.0-flash-lite-preview-02-05:free"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Бот работает!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

@bot.message_handler(func=lambda message: True)
def handle_ai_request(message):
    try:
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
            timeout=30
        )
        
        result = response.json()
        
        # Если пришел правильный ответ
        if 'choices' in result and len(result['choices']) > 0:
            ai_message = result['choices'][0]['message']['content']
            bot.reply_to(message, ai_message)
        else:
            # Если OpenRouter вернул ошибку, мы увидим её в логах Render
            print(f"Ошибка от OpenRouter API: {result}")
            bot.reply_to(message, "ИИ задумался и не ответил. Попробуйте еще раз через минуту.")
            
    except Exception as e:
        print(f"Общая ошибка: {e}")
        bot.reply_to(message, "Произошла техническая ошибка. Проверьте логи сервера.")

if __name__ == "__main__":
    Thread(target=run_web).start()
    print("Бот запущен!")
    # infinity_polling защищает от ошибки 409 Conflict при перезагрузке Render
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
