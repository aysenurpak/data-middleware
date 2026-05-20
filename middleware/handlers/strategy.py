"""
Strategy Pattern - Format Seçim Stratejileri

Her role için farklı formatting stratejisi implementasyonu.
Runtime'da role'e göre doğru strateji seçilir.
"""

from abc import ABC, abstractmethod
import json
import csv
import io
from pathlib import Path


class FormattingStrategy(ABC):
    """Soyut Format Stratejisi"""

    @abstractmethod
    def format(self, log: dict) -> str:
        """Logu belirtilen formatta döndür"""
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Dosya uzantısı"""
        pass

    @abstractmethod
    def get_filename(self) -> str:
        """Dosya adı"""
        pass


class HtmlStrategy(FormattingStrategy):
    """System Admin için HTML Stratejisi"""

    def format(self, log: dict) -> str:
        """HTML formatında log"""
        level = log.get("level", "INFO")
        color_map = {
            "CRITICAL": "#ff4444",
            "ERROR": "#ff8800",
            "WARNING": "#ffcc00",
            "INFO": "#4488ff",
            "DEBUG": "#aaaaaa",
        }
        color = color_map.get(level, "#cccccc")
        tags = ", ".join(log.get("tags", []))

        return f"""
<div class="log-entry" style="border-left: 5px solid {color}; padding: 12px; margin: 8px 0; font-family: monospace; background: #1e1e1e; color: #ddd; border-radius: 4px;">
  <div style="display:flex; justify-content:space-between;">
    <span style="color:{color}; font-weight:bold;">{log.get('severity_label', level)}</span>
    <span style="color:#888;">{log.get('date')} {log.get('time')}</span>
  </div>
  <div style="margin-top:6px;">
    <b>Sender:</b> {log.get('sender_id')} &nbsp;|&nbsp;
    <b>TX:</b> {log.get('transaction_no')}
  </div>
  <div style="margin-top:6px; color:#eee;">
    <b>Mesaj:</b> {log.get('message')}
  </div>
  <div style="margin-top:6px; font-size:0.85em; color:#aaa;">
    <b>Etiketler:</b> {tags} &nbsp;|&nbsp;
    <b>⚡ Aksiyon:</b> {log.get('recommended_action')}
  </div>
  <div style="margin-top:4px; font-size:0.8em; color:#666;">
    Kaynak: {log.get('source_system')} | Middleware: {log.get('middleware_version')}
  </div>
</div>
""".strip()

    def get_file_extension(self) -> str:
        return ".html"

    def get_filename(self) -> str:
        return "system_admin_logs"


class CsvStrategy(FormattingStrategy):
    """Cybersecurity için CSV Stratejisi"""

    def format(self, log: dict) -> str:
        """CSV formatında log"""
        fields = [
            "level",
            "severity_score",
            "severity_label",
            "sender_id",
            "transaction_no",
            "date",
            "time",
            "day_of_week",
            "message",
            "recommended_action",
            "credit_card",
            "email",
            "tc_kimlik",
            "source_system",
            "middleware_version",
        ]

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerow({f: log.get(f, "") for f in fields})

        return output.getvalue().strip()

    def get_file_extension(self) -> str:
        return ".csv"

    def get_filename(self) -> str:
        return "cybersec_logs"


class JsonStrategy(FormattingStrategy):
    """Web Developer için JSON Stratejisi"""

    def format(self, log: dict) -> str:
        """JSON formatında log"""
        json_data = {
            "meta": {
                "source": log.get("source_system"),
                "version": log.get("middleware_version"),
                "enriched_at": log.get("enriched_at"),
            },
            "event": {
                "level": log.get("level"),
                "severity": log.get("severity_label"),
                "score": log.get("severity_score"),
                "action": log.get("recommended_action"),
                "tags": log.get("tags", []),
            },
            "sender": {
                "id": log.get("sender_id"),
                "transaction_no": log.get("transaction_no"),
                "email": log.get("email"),
            },
            "security": {
                "credit_card": log.get("credit_card"),
                "tc_kimlik": log.get("tc_kimlik"),
            },
            "message": log.get("message"),
            "timestamp": {
                "date": log.get("date"),
                "time": log.get("time"),
                "day_of_week": log.get("day_of_week"),
            },
        }
        return json.dumps(json_data, ensure_ascii=False, indent=2)

    def get_file_extension(self) -> str:
        return ".json"

    def get_filename(self) -> str:
        return "web_dev_logs"


class StrategyFactory:
    """Strategy Fabrikası - Rolün göre uygun strateji seç"""

    _strategies = {
        "system_admin": HtmlStrategy(),
        "cybersec": CsvStrategy(),
        "web_dev": JsonStrategy(),
    }

    @staticmethod
    def get_strategy(role: str) -> FormattingStrategy:
        """Rolün göre format stratejisini döndür"""
        return StrategyFactory._strategies.get(role.lower(), StrategyFactory._strategies["web_dev"])
