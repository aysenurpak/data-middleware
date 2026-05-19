import re
from handlers.base_handler import BaseHandler

class AnonymizerHandler(BaseHandler):
    """
    Chain of Responsibility - 1. Halka
    Hassas verileri maskeler: kredi kartı, TC kimlik, e-posta
    """

    def process(self, log: dict) -> dict:
        log = self._mask_credit_card(log)
        log = self._mask_tc_kimlik(log)
        log = self._mask_email(log)
        log = self._mask_in_message(log)
        return log

    # -------- Kredi Kartı --------
    def _mask_credit_card(self, log: dict) -> dict:
        if log.get("credit_card"):
            log["credit_card"] = self._mask_card_number(log["credit_card"])
        return log

    def _mask_card_number(self, card: str) -> str:
        digits = card.replace(" ", "").replace("-", "")
        if len(digits) >= 12:
            return "**** **** **** " + digits[-4:]
        return "****"

    # -------- TC Kimlik --------
    def _mask_tc_kimlik(self, log: dict) -> dict:
        if log.get("tc_kimlik"):
            tc = log["tc_kimlik"]
            if len(tc) == 11:
                log["tc_kimlik"] = tc[:3] + "****" + tc[-4:]
            else:
                log["tc_kimlik"] = "***********"
        return log

    # -------- E-posta --------
    def _mask_email(self, log: dict) -> dict:
        if log.get("email"):
            log["email"] = self._mask_email_address(log["email"])
        return log

    def _mask_email_address(self, email: str) -> str:
        if "@" in email:
            local, domain = email.split("@", 1)
            if len(local) <= 2:
                masked_local = "*" * len(local)
            else:
                masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
            return f"{masked_local}@{domain}"
        return "***@***.***"

    # -------- Mesaj İçindeki Hassas Veri --------
    def _mask_in_message(self, log: dict) -> dict:
        msg = log.get("message", "")

        # Mesaj içindeki kredi kartı numaralarını maskele
        msg = re.sub(
            r"\b(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})\b",
            "**** **** **** ****",
            msg
        )

        # Mesaj içindeki TC kimlik numaralarını maskele
        msg = re.sub(
            r"\b(\d{11})\b",
            "***********",
            msg
        )

        # Mesaj içindeki e-postaları maskele
        msg = re.sub(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "***@***.***",
            msg
        )

        log["message"] = msg
        return log