import requests
import random
import time
import uuid
from faker import Faker

fake = Faker("tr_TR")

MIDDLEWARE_URL = "http://middleware:8000"

# -------- Sabitler --------
LEVELS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
ROLES  = ["system_admin", "cybersec", "web_dev"]

SCENARIOS = [
    # Kritik senaryolar
    {
        "level": "CRITICAL",
        "message": "Borsa sistemi çöktü! Tüm işlemler durduruldu.",
        "has_sensitive": False,
    },
    {
        "level": "CRITICAL",
        "message": "Yetkisiz erişim tespit edildi. Kullanıcı hesabı donduruldu.",
        "has_sensitive": True,
    },
    {
        "level": "CRITICAL",
        "message": "Veritabanı bağlantısı kesildi. Acil müdahale gerekiyor.",
        "has_sensitive": False,
    },
    # Hata senaryoları
    {
        "level": "ERROR",
        "message": "Hisse senedi fiyatı güncellenemedi. Servis yanıt vermiyor.",
        "has_sensitive": False,
    },
    {
        "level": "ERROR",
        "message": "Ödeme işlemi başarısız. Kart bilgisi doğrulanamadı.",
        "has_sensitive": True,
    },
    {
        "level": "ERROR",
        "message": "Kullanıcı kimlik doğrulama hatası. Şüpheli giriş denemesi.",
        "has_sensitive": True,
    },
    # Uyarı senaryoları
    {
        "level": "WARNING",
        "message": "Sunucu bellek kullanımı %85 seviyesine ulaştı.",
        "has_sensitive": False,
    },
    {
        "level": "WARNING",
        "message": "API istek limiti aşılmak üzere. Kalan: 50 istek.",
        "has_sensitive": False,
    },
    # Info senaryoları
    {
        "level": "INFO",
        "message": "Kullanıcı sisteme başarıyla giriş yaptı.",
        "has_sensitive": True,
    },
    {
        "level": "INFO",
        "message": "Günlük borsa raporu oluşturuldu ve iletildi.",
        "has_sensitive": False,
    },
    # Debug senaryoları
    {
        "level": "DEBUG",
        "message": "Cache temizleme işlemi tamamlandı.",
        "has_sensitive": False,
    },
    {
        "level": "DEBUG",
        "message": "Bağlantı havuzu yeniden başlatıldı. Bağlantı sayısı: 10.",
        "has_sensitive": False,
    },
]


# -------- Log Üretici --------
def generate_log(scenario: dict) -> dict:
    log = {
        "level":          scenario["level"],
        "role":           random.choice(ROLES),
        "message":        scenario["message"],
        "sender_id":      f"SND-{fake.bothify('??####').upper()}",
        "transaction_no": str(uuid.uuid4())[:8].upper(),
    }

    if scenario["has_sensitive"]:
        choice = random.choice(["card", "email", "tc", "all"])
        if choice in ("card", "all"):
            log["credit_card"] = fake.credit_card_number(card_type=None)
        if choice in ("email", "all"):
            log["email"] = fake.email()
        if choice in ("tc", "all"):
            log["tc_kimlik"] = fake.bothify("###########", letters="0123456789")

    return log


# -------- Middleware'e Gönder --------
def send_log(log: dict):
    try:
        res = requests.post(f"{MIDDLEWARE_URL}/log", json=log, timeout=5)
        data = res.json()
        fmt  = data.get("output_format", "?")
        lvl  = log["level"]
        sid  = log["sender_id"]
        ms   = data.get("processing_time_ms", "?")
        print(f"[{lvl}] {sid} → {fmt} | {ms}ms ✓")
    except Exception as e:
        print(f"[HATA] Gönderilemedi: {e}")


def send_batch(logs: list):
    try:
        res  = requests.post(f"{MIDDLEWARE_URL}/logs/batch", json=logs, timeout=30)
        data = res.json()
        print(f"[BATCH] {data['total']} log → {data['processing_time_ms']}ms ✓")
    except Exception as e:
        print(f"[BATCH HATA] {e}")


# -------- Ana Akış --------
def run_normal():
    """Tüm senaryoları sırayla gönder"""
    print("\n === NORMAL SENARYO MODU ===")
    for scenario in SCENARIOS:
        log = generate_log(scenario)
        send_log(log)
        time.sleep(0.3)


def run_performance_test(count: int = 500):
    """Yüksek hacimli batch testi"""
    print(f"\n⚡ === PERFORMANS TESTİ ({count} log) ===")
    batch = []
    for _ in range(count):
        scenario = random.choice(SCENARIOS)
        batch.append(generate_log(scenario))

    # 50'lik paketler halinde gönder
    chunk_size = 50
    for i in range(0, len(batch), chunk_size):
        chunk = batch[i:i+chunk_size]
        send_batch(chunk)
        time.sleep(0.1)


if __name__ == "__main__":
    print(" Producer başlatılıyor...")
    print(f" Middleware: {MIDDLEWARE_URL}")

    # Middleware'in ayağa kalkması için bekle
    time.sleep(5)

    # 1. Normal senaryo
    run_normal()

    time.sleep(2)

    # 2. Performans testi
    run_performance_test(count=500)

    print("\n Tüm testler tamamlandı!")