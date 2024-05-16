import os
import json
from PyQt5.QtWidgets import QInputDialog, QApplication  # Added QApplication import
import openai

# Import constants
from constants import API_KEY_FILE

class APIKeyManager:
    def __init__(self, parent=None):
        self.parent = parent
        self.api_key = self.load_api_key()
        if not self.api_key:
            self.ask_for_api_key()

    def load_api_key(self):
        if os.path.exists(API_KEY_FILE):
            with open(API_KEY_FILE, 'r') as file:
                data = json.load(file)
                return data.get('api_key', '')
        return ''

    def ask_for_api_key(self):
        api_key, ok = QInputDialog.getText(self.parent, 'API Key', 'Enter your OpenAI API Key:')
        if ok and api_key:
            self.api_key = api_key
            openai.api_key = api_key
            self.save_api_key(api_key)

    def save_api_key(self, api_key):
        with open(API_KEY_FILE, 'w') as file:
            json.dump({'api_key': api_key}, file)