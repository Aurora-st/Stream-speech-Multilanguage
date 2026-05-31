FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV WHISPER_MODEL=tiny
ENV API_HOST=0.0.0.0
ENV API_PORT=8000
ENV PUBLIC_BASE_URL=http://127.0.0.1:8000
ENV DATABASE_PATH=data/analytics.db

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
