import requests
import random
import time
import uuid
from faker import Faker
from collections import defaultdict
from statistics import mean, stdev

fake = Faker("tr_TR")

MIDDLEWARE_URL = "http://middleware:8000"

# -------- Performance Tracker --------
class PerformanceTracker:
    """İstek performans metrikleri takip eder"""

    def __init__(self):
        self.response_times = []
        self.error_count = 0
        self.success_count = 0
        self.level_times = defaultdict(list)
        self.format_counts = defaultdict(int)

    def add_success(self, response_time_ms: float, level: str, fmt: str):
        """Başarılı bir isteği logla"""
        self.response_times.append(response_time_ms)
        self.success_count += 1
        self.level_times[level].append(response_time_ms)
        self.format_counts[fmt] += 1

    def add_error(self):
        """Hata sayısını artır"""
        self.error_count += 1

    def print_stats(self, test_name: str, total_time: float):
        """Performans istatistiklerini yazdır"""
        total = self.success_count + self.error_count
        if total == 0:
            print(f"\n❌ {test_name}: Veri yok")
            return

        print(f"\n{'=' * 70}")
        print(f"📊 {test_name} - PERFORMANS İSTATİSTİKLERİ")
        print(f"{'=' * 70}")

        # Genel istatistikler
        print(f"\n🔢 GENEL:")
        print(f"   Total İstek: {total}")
        print(f"   Başarı: {self.success_count} ({100*self.success_count/total:.1f}%)")
        print(f"   Hata: {self.error_count}")
        print(f"   Toplam Süre: {total_time:.2f}s")

        if self.success_count == 0:
            print("   ⚠️ Başarılı istek yok")
            return

        # Response time istatistikleri
        min_time = min(self.response_times)
        max_time = max(self.response_times)
        avg_time = mean(self.response_times)
        p95_time = sorted(self.response_times)[int(len(self.response_times) * 0.95)]

        print(f"\n⏱️  RESPONSE TIME (ms):")
        print(f"   Min: {min_time:.2f}ms")
        print(f"   Max: {max_time:.2f}ms")
        print(f"   Avg: {avg_time:.2f}ms")
        print(f"   P95: {p95_time:.2f}ms")
        if len(self.response_times) > 1:
            stddev = stdev(self.response_times)
            print(f"   StdDev: {stddev:.2f}ms")

        # Throughput
        throughput = self.success_count / total_time if total_time > 0 else 0
        print(f"\n🚀 THROUGHPUT:")
        print(f"   Requests/sec: {throughput:.2f}")
        print(f"   Logs/sec: {throughput:.2f}")

        # Level bazında istatistikler
        if self.level_times:
            print(f"\n📈 SEVIYE BAZLI:")
            for level in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]:
                if level in self.level_times:
                    times = self.level_times[level]
                    print(f"   {level:10s}: {len(times):3d} req, "
                          f"avg {mean(times):6.2f}ms, "
                          f"min {min(times):6.2f}ms, "
                          f"max {max(times):6.2f}ms")

        # Format bazında istatistikler
        if self.format_counts:
            print(f"\n📋 FORMAT BAZLI:")
            for fmt, count in sorted(self.format_counts.items()):
                print(f"   {fmt:6s}: {count:4d} ({100*count/self.success_count:.1f}%)")

        print(f"{'=' * 70}\n")

    def reset(self):
        """İstatistikleri sıfırla"""
        self.response_times = []
        self.error_count = 0
        self.success_count = 0
        self.level_times = defaultdict(list)
        self.format_counts = defaultdict(int)


tracker = PerformanceTracker()

# -------- Sabitler --------
LEVELS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
ROLES = ["system_admin", "cybersec", "web_dev"]

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
        fmt = data.get("output_format", "?")
        lvl = log["level"]
        sid = log["sender_id"]
        ms = data.get("processing_time_ms", 0)
        tracker.add_success(ms, lvl, fmt)
        print(f"[{lvl}] {sid} → {fmt} | {ms}ms ✓")
    except Exception as e:
        tracker.add_error()
        print(f"[ERROR] Could not send: {e}")


def send_batch(logs: list) -> float:
    """Batch log'ları gönder ve toplam süreyi döndür"""
    try:
        res = requests.post(f"{MIDDLEWARE_URL}/logs/batch", json=logs, timeout=30)
        data = res.json()
        total_time = data.get("processing_time_ms", 0)
        
        # Her bir log için istatistik ekle
        for log in logs:
            tracker.add_success(total_time / len(logs), log["level"], "JSON")
        
        print(f"[BATCH] {data['total']} logs → {total_time}ms ✓")
        return total_time
    except Exception as e:
        tracker.add_error()
        print(f"[BATCH ERROR] {e}")
        return 0


# -------- Ana Akış --------
def run_normal():
    """Tüm senaryoları sırayla gönder"""
    print("\n" + "="*70)
    print("📋 NORMAL SENARYO MODU - Tüm senaryolar sırayla test edilecek")
    print("="*70)
    
    tracker.reset()
    start_time = time.time()
    
    for scenario in SCENARIOS:
        log = generate_log(scenario)
        send_log(log)
        time.sleep(0.3)
    
    elapsed = time.time() - start_time
    tracker.print_stats("Normal Senaryo", elapsed)


def run_performance_test(count: int = 500):
    """Yüksek hacimli batch testi"""
    print("\n" + "="*70)
    print(f"⚡ PERFORMANS TESTİ - {count} log gönderilecek")
    print("="*70)
    
    tracker.reset()
    start_time = time.time()
    
    batch = []
    for _ in range(count):
        scenario = random.choice(SCENARIOS)
        batch.append(generate_log(scenario))

    # 50'lik paketler halinde gönder
    chunk_size = 50
    for i in range(0, len(batch), chunk_size):
        chunk = batch[i : i + chunk_size]
        send_batch(chunk)
        time.sleep(0.1)

    elapsed = time.time() - start_time
    tracker.print_stats(f"Performans Testi ({count} logs)", elapsed)


def run_stress_test(duration_seconds: int = 10):
    """Uzun süreli stress test"""
    print("\n" + "="*70)
    print(f"💥 STRESS TESTİ - {duration_seconds} saniye boyunca maksimum yük")
    print("="*70)
    
    tracker.reset()
    start_time = time.time()
    
    while time.time() - start_time < duration_seconds:
        batch = []
        for _ in range(100):
            scenario = random.choice(SCENARIOS)
            batch.append(generate_log(scenario))
        
        send_batch(batch)
    
    elapsed = time.time() - start_time
    tracker.print_stats(f"Stress Test ({duration_seconds}s)", elapsed)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 PRODUCER BAŞLATILIYOR")
    print("="*70)
    print(f"📍 Middleware: {MIDDLEWARE_URL}")

    # Middleware'in ayağa kalkması için bekle
    print("⏳ Middleware'in başlaması için 5 saniye bekleniyor...")
    time.sleep(5)

    try:
        # 1. Normal senaryo
        run_normal()
        time.sleep(3)

        # 2. Performans testi
        run_performance_test(count=500)
        time.sleep(3)

        # 3. Stress test
        run_stress_test(duration_seconds=10)

        print("\n" + "="*70)
        print("✅ Tüm testler tamamlandı!")
        print("="*70)

    except KeyboardInterrupt:
        print("\n\n⛔ Test kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"\n\n❌ Beklenmeyen hata: {e}")