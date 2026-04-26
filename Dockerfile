FROM python:3.9-slim

WORKDIR /app

RUN pip install --no-cache-dir pycryptodome && \
    apt-get update && apt-get install -y curl

RUN curl -L https://raw.githubusercontent.com/alexbers/mtprotoproxy/master/mtprotoproxy.py -o proxy.py

ENV PYTHONUNBUFFERED=1

EXPOSE 10000

# Попробуем маскировку под cloudflare.com — это часто помогает обойти фильтры
CMD ["python3", "proxy.py", "10000", "d0d6e111bada5511fcce9584deadbeef", "00000000000000000000000000000000", "", "www.cloudflare.com"]
