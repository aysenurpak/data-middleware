# Python 3.11 slim imajı kullan
FROM python:3.11-slim

# Çalışma dizini
WORKDIR /app

# Önce requirements kopyala (Docker cache için)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# Producer'ı başlat
CMD ["python", "producer.py"]