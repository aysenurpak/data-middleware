import json
import csv
import io
from handlers.base_handler import BaseHandler


class FormatterHandler(BaseHandler):
    """
    Chain of Responsibility - 3. Halka
    Role'e göre farklı format üretir:
      - system_admin → HTML
      - cybersec     → CSV
      - web_dev      → JSON
    """

    def process(self, log: dict) -> dict:
        role = log.get("role", "web_dev").lower()

        if role == "system_admin":
            log["formatted_output"] = self._to_html(log)
            log["output_format"] = "HTML"
        elif role == "cybersec":
            log["formatted_output"] = self._to_csv(log)
            log["output_format"] = "CSV"
        else:
            log["formatted_output"] = self._to_json(log)
            log["output_format"] = "JSON"

        return log

    # -------- HTML (System Admin) --------
    def _to_html(self, log: dict) -> str:
        level = log.get("level", "INFO")
        color_map = {
            "CRITICAL": "#ff4444",
            "ERROR":    "#ff8800",
            "WARNING":  "#ffcc00",
            "INFO":     "#4488ff",
            "DEBUG":    "#aaaaaa",
        }
        color = color_map.get(level, "#cccccc")
        tags  = ", ".join(log.get("tags", []))

        return f"""
<div class="log-entry" style="border-left: 5px solid {color}; padding: 12px; margin: 8px 0; font-family: monospace; background: #1e1e1e; color: #ddd; border-radius: 4px;">
  <div style="display:flex; justify-content:space-between;">
    <span style="color:{color}; font-weight:bold;">{log.get('severity_label', level)}</span>
    <span style="color:#888;">{log.get('date')} {log.get('time')}</span>
  </div>
  <div style="margin-top:6px;">
    <b> Sender:</b> {log.get('sender_id')} &nbsp;|&nbsp;
    <b> TX:</b> {log.get('transaction_no')}
  </div>
  <div style="margin-top:6px; color:#eee;">
    <b> Mesaj:</b> {log.get('message')}
  </div>
  <div style="margin-top:6px; font-size:0.85em; color:#aaa;">
    <b> Etiketler:</b> {tags} &nbsp;|&nbsp;
    <b>⚡ Aksiyon:</b> {log.get('recommended_action')}
  </div>
  <div style="margin-top:4px; font-size:0.8em; color:#666;">
    Kaynak: {log.get('source_system')} | Middleware: {log.get('middleware_version')}
  </div>
</div>
""".strip()

    # -------- CSV (Cybersec) --------
    def _to_csv(self, log: dict) -> str:
        fields = [
            "level", "severity_score", "severity_label",
            "sender_id", "transaction_no",
            "date", "time", "day_of_week",
            "message", "recommended_action",
            "credit_card", "email", "tc_kimlik",
            "source_system", "middleware_version"
        ]

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=fields,
            extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerow({f: log.get(f, "") for f in fields})

        return output.getvalue().strip()

    # -------- JSON (Web Dev) --------
    def _to_json(self, log: dict) -> str:
        json_data = {
            "meta": {
                "source":     log.get("source_system"),
                "version":    log.get("middleware_version"),
                "enriched_at": log.get("enriched_at"),
            },
            "event": {
                "level":      log.get("level"),
                "severity":   log.get("severity_label"),
                "score":      log.get("severity_score"),
                "action":     log.get("recommended_action"),
                "tags":       log.get("tags", []),
            },
            "sender": {
                "id":             log.get("sender_id"),
                "transaction_no": log.get("transaction_no"),
                "email":          log.get("email"),
            },
            "security": {
                "credit_card": log.get("credit_card"),
                "tc_kimlik":   log.get("tc_kimlik"),
            },
            "message": log.get("message"),
            "timestamp": {
                "date":        log.get("date"),
                "time":        log.get("time"),
                "day_of_week": log.get("day_of_week"),
            }
        }
        return json.dumps(json_data, ensure_ascii=False, indent=2)