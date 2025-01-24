from django.core.mail.backends.smtp import EmailBackend
import ssl
import smtplib

class CustomEmailBackend(EmailBackend):
    def open(self):
        """Открыть соединение с сервером."""
        if self.connection:
            return False
        try:
            # Создаем контекст с отключенной проверкой SSL
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            # Подключение к серверу
            self.connection = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
            self.connection.ehlo()
            if self.use_tls:
                self.connection.starttls(context=ssl_context)
                self.connection.ehlo()
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception:
            if not self.fail_silently:
                raise
            return False
