# Python 3.11 slim imajı kullan
FROM python:3.11-slim

# Çalışma dizini
WORKDIR /app

# Önce requirements kopyala (Docker cache için)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodlarını kopyala
COPY . .

# Output klasörü oluştur
RUN mkdir -p /app/output

# Port aç
EXPOSE 8000

# Sunucuyu başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]