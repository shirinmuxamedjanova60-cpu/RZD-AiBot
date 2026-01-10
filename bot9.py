import telebot
import requests
import json
import os
from flask import Flask
from threading import Thread

# --- НАСТРОЙКИ (Данные из Render Environment Variables) ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OPENROUTER_KEY = os.environ.get('OPENROUTER_KEY')
# Используем самую актуальную бесплатную модель
MODEL_NAME = "google/gemini-2.0-flash-lite-preview-02-05:free"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask('')

# --- ВЕБ-СЕРВЕР ДЛЯ ПОДДЕРЖАНИЯ ЖИЗНИ (RENDER + CRON-JOB) ---
@app.route('/')
def home():
    return "Бот RZDBot активен и работает!"

def run_web():
    # Порт 8080 стандартный для Render
    app.run(host='0.0.0.0', port=8080)

# --- ОБРАБОТКА СООБЩЕНИЙ ---
@bot.message_handler(func=lambda message: True)
def handle_ai_request(message):
    # Выводим в логи каждое полученное сообщение для отладки
    print(f"--- НОВОЕ СООБЩЕНИЕ: {message.text} ---")
    
    try:
        # Отправляем запрос в OpenRouter
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://render.com", # Обязательно для некоторых моделей
                "X-Title": "RZDBot"
            },
            data=json.dumps({
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": message.text}]
            }),
            timeout=30
        )
        
        # Печатаем техническую информацию в логи Render
        print(f"Статус ответа OpenRouter: {response.status_code}")
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            ai_message = result['choices'][0]['message']['content']
            bot.reply_to(message, ai_message)
            print("Ответ успешно отправлен пользователю.")
        else:
            # Если что-то не так, мы увидим полную причину в логах
            print(f"ПОЛНЫЙ ТЕКСТ ОШИБКИ ОТ API: {result}")
            bot.reply_to(message, "ИИ задумался и не ответил. Попробуйте еще раз через минуту.")
            
    except Exception as e:
        print(f"Критическая ошибка в коде: {e}")
        bot.reply_to(message, "Произошла техническая ошибка. Посмотрите логи сервера.")

# --- ЗАПУСК ПРИЛОЖЕНИЯ ---
if __name__ == "__main__":
    # 1. Запускаем сервер Flask в отдельном потоке
    server_thread = Thread(target=run_web)
    server_thread.daemon = True
    server_thread.start()
    
    print("Бот запущен и готов к работе!")
    
    # 2. Бесконечный опрос Telegram с защитой от ошибок
    # Используем infinity_polling, чтобы бот не падал при ошибке 409
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
