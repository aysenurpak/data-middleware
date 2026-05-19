from datetime import datetime
from handlers.base_handler import BaseHandler


class EnricherHandler(BaseHandler):
    """
    Chain of Responsibility - 2. Halka
    Loglara metadata ve etiketler ekler.
    """

    # Kritiklik seviyeleri
    SEVERITY_MAP = {
        "CRITICAL": {"score": 5, "label": "🔴 KRİTİK",    "action": "IMMEDIATE_ACTION"},
        "ERROR":    {"score": 4, "label": "🟠 HATA",       "action": "INVESTIGATE"},
        "WARNING":  {"score": 3, "label": "🟡 UYARI",      "action": "MONITOR"},
        "INFO":     {"score": 2, "label": "🔵 BİLGİ",      "action": "LOG_ONLY"},
        "DEBUG":    {"score": 1, "label": "⚪ DEBUG",       "action": "LOG_ONLY"},
    }

    def process(self, log: dict) -> dict:
        log = self._add_timestamp(log)
        log = self._add_severity(log)
        log = self._add_transaction_meta(log)
        log = self._add_tags(log)
        return log

    # -------- Zaman Damgası --------
    def _add_timestamp(self, log: dict) -> dict:
        now = datetime.now()
        log["enriched_at"]  = now.isoformat()
        log["date"]         = now.strftime("%Y-%m-%d")
        log["time"]         = now.strftime("%H:%M:%S")
        log["day_of_week"]  = now.strftime("%A")
        return log

    # -------- Kritiklik Seviyesi --------
    def _add_severity(self, log: dict) -> dict:
        level = log.get("level", "INFO").upper()
        severity = self.SEVERITY_MAP.get(level, self.SEVERITY_MAP["INFO"])

        log["severity_score"]  = severity["score"]
        log["severity_label"]  = severity["label"]
        log["recommended_action"] = severity["action"]
        return log

    # -------- Transaction Metadata --------
    def _add_transaction_meta(self, log: dict) -> dict:
        log["sender_id"]       = log.get("sender_id") or "UNKNOWN"
        log["transaction_no"]  = log.get("transaction_no") or "N/A"
        log["source_system"]   = "STOCK_EXCHANGE_v1"
        log["middleware_version"] = "1.0.0"
        return log

    # -------- Etiketler --------
    def _add_tags(self, log: dict) -> dict:
        tags = ["borsa", "middleware"]
        level = log.get("level", "").upper()

        if level == "CRITICAL":
            tags += ["alert", "urgent", "notify-team"]
        elif level == "ERROR":
            tags += ["error", "needs-review"]
        elif level == "WARNING":
            tags += ["warning", "watch"]

        if log.get("credit_card"):
            tags.append("financial-data")
        if log.get("email"):
            tags.append("personal-data")
        if log.get("tc_kimlik"):
            tags.append("identity-data")

        log["tags"] = tags
        return log