import logging
import smtplib
from email.mime.text import MIMEText

class Notifier:
    def __init__(self, config=None):
        self.config = config or {}
        self.logger = logging.getLogger("Notifier")
        self.telegram_enabled = self.config.get("telegram_enabled", False)
        self.email_enabled = self.config.get("email_enabled", False)

    def alert(self, message, level="WARNING"):
        msg = f"[{level}] AutoBot Alert: {message}"
        self.logger.warning(msg)
        
        if self.telegram_enabled:
            self._send_telegram(msg)
        if self.email_enabled:
            self._send_email(msg)

    def _send_telegram(self, message):
        # Placeholder for Telegram API call
        # requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": chat_id, "text": message})
        self.logger.info(f"Telegram alert sent: {message}")

    def _send_email(self, message):
        # Placeholder for SMTP email sending
        self.logger.info(f"Email alert sent: {message}")
