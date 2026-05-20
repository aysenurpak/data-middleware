# 📊 Stock Exchange Middleware - CENG302 Final Project

![Status](https://img.shields.io/badge/Status-Complete-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-lightblue)
![License](https://img.shields.io/badge/License-Academic-orange)

Borsa kuruluşu için veri işleme ara katmanı (middleware) yazılımı. Sistem, güvenlik maskeleme, log zenginleştirme ve rol bazlı format dönüşümü işlemlerini gerçekleştirmektedir.

---

## 🎯 Proje Hedefleri

- ✅ **Güvenlik**: Hassas verileri (kredi kartı, TC kimlik, e-posta) maskeleme
- ✅ **Zenginleştirme**: Loglara metadata ve etiketler ekleme
- ✅ **Biçim Dönüşümü**: Rolün göre (HTML, CSV, JSON) formatlama
- ✅ **Performans**: Yüksek throughput ile batch işleme
- ✅ **Tasarım Kalıpları**: Chain of Responsibility + Strategy Pattern

---

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────┐
│     Producer Container      │
│  • 12 Farklı Test Senaryo  │
│  • 500 Log Batch Test      │
│  • 10s Stress Test         │
│  • Performance Metrics     │
└──────────────┬──────────────┘
               │ HTTP POST
               ▼
        ┌──────────────┐
        │  exchange-net│ (Docker Network)
        └──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Middleware Container (FastAPI)
│                             │
│ 1. AnonymizerHandler        │
│    ↓ (Maskeleme)            │
│ 2. EnricherHandler          │
│    ↓ (Metadata Ekleme)      │
│ 3. FormatterHandler         │
│    ↓ (Format Seçim)         │
│                             │
│ Output Files:               │
│ • system_admin_logs.html    │
│ • cybersec_logs.csv         │
│ • web_dev_logs.json         │
└─────────────────────────────┘
```

---

## 🚀 Hızlı Başlangıç

### Gereksinimler

```bash
• Docker & Docker Compose
• Python 3.11+ (lokal test için)
• 2GB RAM (minimum)
```

### Docker ile Çalıştırma

```bash
# Repository'yi clone et
git clone https://github.com/aysenurpak/data-middleware.git
cd data-middleware

# Docker Daemon'u başlat (macOS)
open /Applications/Docker.app

# Containers'ı build et ve başlat
docker-compose up --build

# Çıktıyı görüntüle (yeni terminal)
docker exec middleware cat /app/output/system_admin_logs.html
docker exec middleware cat /app/output/cybersec_logs.csv
docker exec middleware python -m json.tool /app/output/web_dev_logs.json | head -30
```

### Lokal Test (Python)

```bash
# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Dependencies kur
cd middleware && pip install -r requirements.txt
cd ../producer && pip install -r requirements.txt

# Syntax kontrol
python -m py_compile middleware/main.py middleware/handlers/*.py producer/producer.py
```

---

## 📋 Tasarım Kalıpları

### 1. Chain of Responsibility (Zincir Sorumluluk)

Handler'lar bir zincir oluşturarak sırayla işlem yapması sağlanır:

**Dosya:** [middleware/handlers/base_handler.py](middleware/handlers/base_handler.py)

```python
# Zincir kurulması
anonymizer = AnonymizerHandler()
enricher = EnricherHandler()
formatter = FormatterHandler()

anonymizer.set_next(enricher).set_next(formatter)

# Kullanım
result = anonymizer.handle(log)
```

**Handler'lar:**

1. **AnonymizerHandler** - Hassas verileri maskleme
2. **EnricherHandler** - Metadata ekleme
3. **FormatterHandler** - Format seçimi (Chain'i kontrol eder)

### 2. Strategy Pattern (Strateji)

Role'e göre farklı formatting stratejileri runtime'da seçilir:

**Dosya:** [middleware/handlers/strategy.py](middleware/handlers/strategy.py)

```python
# Strateji seçimi
strategy = StrategyFactory.get_strategy(role)
formatted = strategy.format(log)
```

**Stratejiler:**

- `HtmlStrategy` - System Admin için (`<div>` tabanlı HTML)
- `CsvStrategy` - Cybersecurity için (Yapılandırılmış CSV)
- `JsonStrategy` - Web Developer için (REST API JSON)

---

## 📊 Performans Metrikleri

Test Sonuçları (30 saniye süresinde):

| Test             | İstek Sayısı | Avg Response | Throughput   | Success |
| ---------------- | ------------ | ------------ | ------------ | ------- |
| **Normal**       | 12           | 62.14ms      | 2.85 req/s   | 100%    |
| **Batch (500)**  | 500          | 21.08ms      | 47.44 req/s  | 100%    |
| **Stress (10s)** | 2000         | 50.67ms      | 197.63 req/s | 99.9%   |

**Detaylı Sonuçlar:** [docs/report.md](docs/report.md)

---

## 📁 Proje Yapısı

```
data-middleware/
├── README.md                      # Bu dosya
├── docker-compose.yml             # Docker servis tanımı
│
├── docs/
│   └── report.md                 # Detaylı proje raporu
│
├── middleware/                   # Ara katman servisi
│   ├── Dockerfile
│   ├── main.py                   # FastAPI uygulaması
│   ├── requirements.txt
│   │
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── base_handler.py       # Soyut handler (Chain of Responsibility)
│   │   ├── anonymizer.py         # Güvenlik maskeleme
│   │   ├── enricher.py           # Metadata zenginleştirme
│   │   ├── formatter.py          # Format dönüşümü
│   │   └── strategy.py           # Strategy Pattern
│   │
│   └── output/                   # Çıktı dosyaları
│       ├── system_admin_logs.html
│       ├── cybersec_logs.csv
│       └── web_dev_logs.json
│
└── producer/                     # Log üretici servisi
    ├── Dockerfile
    ├── producer.py               # Veri üreticisi & test runner
    └── requirements.txt
```

---

## 🔐 Güvenlik - Anonymizer Handler

Hassas verilerin maskelenmesi:

### Kredi Kartı

```
Giriş:  "1234567890123456"
Çıkış:  "**** **** **** 3456"
```

### TC Kimlik

```
Giriş:  "12345678901"
Çıkış:  "123****8901"
```

### E-posta

```
Giriş:  "john@example.com"
Çıkış:  "j***n@example.com"
```

### Mesaj İçindeki Hassas Veriler

Regex kullanarak metinde bulunan:

- Kredi kartı numaraları
- 11 haneli TC kimlik numaraları
- E-posta adresleri

Otomatik olarak maskelenir.

---

## 📝 Zenginleştirme - Enricher Handler

Logları daha verimli hale getirmek için eklenen metadata:

```json
{
  "enriched_at": "2026-05-20T16:30:45.123456",
  "date": "2026-05-20",
  "time": "16:30:45",
  "day_of_week": "Tuesday",

  "severity_score": 4,
  "severity_label": "🟠 HATA",
  "recommended_action": "INVESTIGATE",

  "tags": ["borsa", "middleware", "error", "needs-review"],
  "source_system": "STOCK_EXCHANGE_v1",
  "middleware_version": "1.0.0"
}
```

---

## 🎨 Biçim Özelleştirme - Formatter Handler

### System Admin → HTML

```html
<div class="log-entry" style="border-left: 5px solid #ff8800; ...">
  <span style="color:#ff8800; font-weight:bold;">🟠 HATA</span>
  <span>2026-05-20 16:30:45</span>
  ...
</div>
```

### Cybersecurity → CSV

```csv
level,severity_score,sender_id,transaction_no,message,credit_card,email
ERROR,4,SND-AB1234,TX-xyz789,Hata mesajı,****...****,j***n@...
```

### Web Developer → JSON

```json
{
  "meta": {
    "source": "STOCK_EXCHANGE_v1",
    "version": "1.0.0",
    "enriched_at": "2026-05-20T16:30:45.123456"
  },
  "event": {
    "level": "ERROR",
    "severity": "🟠 HATA",
    "score": 4,
    "tags": ["borsa", "error"]
  },
  "message": "Hata mesajı",
  ...
}
```

---

## 🧪 API Endpoints

### GET /

Health check endpoint

```bash
curl http://localhost:8000/
# {"status": "Middleware is running and ready to receive logs."}
```

### POST /log

Tek bir log işle

```bash
curl -X POST http://localhost:8000/log \
  -H "Content-Type: application/json" \
  -d '{
    "level": "ERROR",
    "role": "web_dev",
    "message": "Error occurred",
    "credit_card": "1234 5678 9012 3456"
  }'
```

### POST /logs/batch

Batch olarak logları işle

```bash
curl -X POST http://localhost:8000/logs/batch \
  -H "Content-Type: application/json" \
  -d '[
    {"level": "ERROR", "role": "web_dev", "message": "Error 1", ...},
    {"level": "INFO", "role": "system_admin", "message": "Info 1", ...}
  ]'
```

---

## 🧑‍💻 Geliştirme Notları

### Environment Değişkenleri

- `MIDDLEWARE_URL` - Middleware endpoint (varsayılan: `http://middleware:8000`)

### Logging

Her istek için detaylı log:

```
[ERROR] SND-AB1234 → JSON | 45.32ms ✓
[BATCH] 50 logs → 1234ms ✓
```

### Hata Yönetimi

- Timeout: 5s (single), 30s (batch)
- Error tracking: Success/error count
- Retry logic: None (best-effort)

---

## 📹 Video Sunumu

Proje videosu şu başlıkları kapsayacak:

1. **Sistem Mimarisi** - Docker, Network, Servisler
2. **Tasarım Kalıpları** - Chain of Responsibility, Strategy
3. **Güvenlik & Zenginleştirme** - Maske, Metadata
4. **Format Dönüşümü** - HTML/CSV/JSON örnekleri
5. **Performans Testi** - Sonuçlar ve analiz

---

## 🤖 Yapay Zeka Kullanımı

Bu projede aşağıdaki amaçlarla yapay zeka yardımı alınmıştır:

- Handler şablonları oluşturma
- Test senaryo brainstorming
- Performance analizi yorumları
- Dokumentasyon yazımı

Ancak, temel mimari, algoritmaları ve implementasyon tamamen manuel olarak geliştirilmiştir.

---

## 📚 Kaynaklar

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Design Patterns: Elements of Reusable Object-Oriented Software](https://en.wikipedia.org/wiki/Design_Patterns)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Python Logging Best Practices](https://docs.python.org/3/library/logging.html)

---

## 📝 Lisans

Bu proje CENG302 Dönem Sonu Ödevi için oluşturulmuştur.

---

## ✅ Kontrol Listesi

- [x] Chain of Responsibility Pattern
- [x] Strategy Pattern
- [x] Güvenlik (Maskeleme)
- [x] Zenginleştirme (Metadata)
- [x] Biçim Özelleştirme (HTML/CSV/JSON)
- [x] Docker Compose Setup
- [x] Performance Testing
- [x] Detaylı Rapor
- [x] README Dokumentasyonu

---

**Geliştirici**: Ayşenur  
**Proje Tarihi**: 20 Mayıs 2026  
**Son Güncelleme**: 20 Mayıs 2026  
**Durum**: ✅ Tamamlandı

---

## 🆘 Sorun Giderme

### Docker Daemon Çalışmıyor (macOS)

```bash
# Docker Desktop'ı aç
open /Applications/Docker.app

# veya terminal üzerinden
docker run --rm hello-world
```

### Port Çakışması

```bash
# Ports'u kontrol et
lsof -i :8000

# Port numarasını değiştir (docker-compose.yml)
ports:
  - "8001:8000"  # 8000 yerine 8001 kullan
```

### Memory Hatası

```bash
# Docker'a daha fazla RAM ayır
# Docker Desktop → Preferences → Resources → Memory → 4GB+ olarak ayarla
```

---

Sorularınız için: [GitHub Issues](https://github.com/aysenurpak/data-middleware/issues)
