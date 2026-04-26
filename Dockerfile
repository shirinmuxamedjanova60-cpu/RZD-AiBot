FROM python:3.9-slim

WORKDIR /app

# Устанавливаем зависимости и инструменты
RUN pip install --no-cache-dir pycryptodome && \
    apt-get update && apt-get install -y curl

# Скачиваем скрипт прокси
RUN curl -L https://raw.githubusercontent.com/alexbers/mtprotoproxy/master/mtprotoproxy.py -o proxy.py

# Указываем Python не буферизировать логи (чтобы сразу видеть ошибки в панели Render)
ENV PYTHONUNBUFFERED=1

# Порт, который мы укажем в настройках Render
EXPOSE 10000

# Запуск: ПОРТ, СЕКРЕТ, ТЕГ(нули)
# Здесь мы НЕ используем домен маскировки для максимальной простоты
CMD ["python3", "proxy.py", "10000", "d0d6e111bada5511fcce9584deadbeef", "00000000000000000000000000000000"]
