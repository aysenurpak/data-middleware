from pathlib import Path
from handlers.base_handler import BaseHandler
from handlers.strategy import StrategyFactory


class FormatterHandler(BaseHandler):
    """
    Chain of Responsibility - 3. Halka
    Strategy Pattern kullanarak role'e göre format seçer:
      - system_admin → HTML (HtmlStrategy)
      - cybersec     → CSV (CsvStrategy)
      - web_dev      → JSON (JsonStrategy)
    """

    def process(self, log: dict) -> dict:
        role = log.get("role", "web_dev").lower()

        # Strategy Pattern: Rolün göre doğru stratejiyı seç
        strategy = StrategyFactory.get_strategy(role)
        log["formatted_output"] = strategy.format(log)
        log["output_format"] = strategy.get_file_extension()[1:].upper()

        # Dosyaya yaz
        self._save_to_file(log, strategy)

        return log

    # -------- Dosya Çıktısı --------
    def _save_to_file(self, log: dict, strategy) -> None:
        """Stratejinin belirttiği dosyaya yaz"""
        output_dir = Path("/app/output")
        output_dir.mkdir(exist_ok=True)

        filename = f"{strategy.get_filename()}{strategy.get_file_extension()}"
        file_path = output_dir / filename

        try:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(log["formatted_output"] + "\n")
        except Exception as e:
            print(f"[DOSYA HATA] {file_path}: {e}")