import os
from src.main import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'production')
