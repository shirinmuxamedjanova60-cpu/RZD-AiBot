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
    return "Бот запущен и работает!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

# 1. Мгновенное приветствие на команду /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "Привет! 😊 Я твой ИИ-помощник. Напиши мне любой вопрос, и я отвечу простым текстом!"
    bot.reply_to(message, welcome_text)

# 2. Основная обработка сообщений
@bot.message_handler(func=lambda message: True)
def handle_ai_request(message):
    try:
        # Добавляем инструкцию к запросу пользователя, чтобы убрать символы разметки
        prompt = f"Отвечай максимально просто, без использования символов Markdown (*, #, _, `). Текст запроса: {message.text}"
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://render.com",
                "X-Title": "RZDAiBot"
            },
            data=json.dumps({
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}]
            }),
            timeout=30
        )
        
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            ai_message = result['choices'][0]['message']['content']
            
            # Очищаем ответ от возможных остатков спецсимволов вручную
            clean_message = ai_message.replace('*', '').replace('#', '').replace('_', '').strip()
            
            if clean_message:
                bot.reply_to(message, clean_message)
            else:
                bot.reply_to(message, "ИИ прислал пустой ответ, попробуйте спросить иначе.")
        else:
            error_text = result.get('error', {}).get('message', 'Ошибка API')
            bot.reply_to(message, f"Ошибка: {error_text}")
            
    except Exception as e:
        bot.reply_to(message, f"Техническая ошибка: {str(e)}")

if __name__ == "__main__":
    # Запуск сервера для Render
    Thread(target=run_web).start()
    
    print("Бот успешно запущен!")
    # infinity_polling автоматически восстанавливает связь при сбоях
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
