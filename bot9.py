import telebot
import requests
import json
import os
from flask import Flask
from threading import Thread

# --- Настройки из Advanced ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OPENROUTER_KEY = os.environ.get('OPENROUTER_KEY')
MODEL_NAME = "google/gemini-2.0-flash-lite-preview-02-05:free"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask('')

# Это нужно, чтобы Render видел, что сервис "жив"
@app.route('/')
def home():
    return "I am alive"

def run_web():
    app.run(host='0.0.0.0', port=8080)

@bot.message_handler(func=lambda message: True)
def handle_ai_request(message):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            data=json.dumps({
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": message.text}]
            })
        )
        ai_message = response.json()['choices'][0]['message']['content']
        bot.reply_to(message, ai_message)
    except Exception as e:
        print(f"Error: {e}")

# Запускаем веб-сервер в отдельном потоке
Thread(target=run_web).start()

# Запускаем бота
print("Бот запущен!")
bot.polling(non_stop=True)
