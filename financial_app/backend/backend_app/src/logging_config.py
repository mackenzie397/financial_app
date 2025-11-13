import logging
import re
import os
import logging.handlers

class NoSensitiveDataFilter(logging.Filter):
    SENSITIVE_FIELDS = ['password', 'email', 'token', 'access_token', 'jwt_secret_key', 'secret_key']

    def filter(self, record):
        message = record.getMessage()
        for field in self.SENSITIVE_FIELDS:
            message = re.sub(r"(\'" + field + r"\':\s*)\'[^\']*\'", r"\1\'[REDACTED]\'", message)
            message = re.sub(r'("' + field + r'":\s*)"[^"]*"', r'\1"[REDACTED]"', message)
        record.msg = message
        return True

def setup_logging(app):
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.handlers.RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        file_handler.addFilter(NoSensitiveDataFilter())
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Financial App startup')
