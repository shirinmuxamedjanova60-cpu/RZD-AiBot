FROM python:3.9-slim

WORKDIR /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir pycryptodome

# Скачиваем скрипт прокси
ADD https://raw.githubusercontent.com/alexbers/mtprotoproxy/master/mtprotoproxy.py /app/proxy.py

ENV PYTHONUNBUFFERED=1

# Render выдает порт динамически через переменную $PORT
# Но мы зафиксируем его для стабильности или используем переменную
EXPOSE 10000

CMD ["python3", "proxy.py", "10000", "d0d6e111bada5511fcce9584deadbeef", "00000000000000000000000000000000", "", "itunes.apple.com"]
