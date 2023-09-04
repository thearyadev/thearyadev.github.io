FROM python:3.11-slim

WORKDIR /aryankothari.dev

COPY requirements.txt .

LABEL org.opencontainers.image.source=https://github.com/thearyadev/aryankothari.dev
LABEL org.opencontainers.image.description="Docker image for aryankothari.dev"
LABEL org.opencontainers.image.licenses=MIT

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]