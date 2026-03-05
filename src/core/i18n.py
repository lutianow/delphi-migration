# src/core/i18n.py

import json
import os
import sys

class I18N:
    def __init__(self, lang='en'):
        self.lang = lang.lower()
        self.translations = {}
        self.load_translations()

    def get_base_path(self):
        # Support PyInstaller paths (sys._MEIPASS vs real path)
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, 'src')
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def load_translations(self):
        base_dir = self.get_base_path()
        locales_dir = os.path.join(base_dir, 'locales')
        file_path = os.path.join(locales_dir, f"{self.lang}.json")
        
        # Fallback to English if file not compiled / missing
        if not os.path.exists(file_path):
            file_path = os.path.join(locales_dir, "en.json")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except Exception:
            self.translations = {}

    def set_language(self, lang):
        self.lang = lang.lower().replace('português', 'pt').replace('english', 'en')
        self.load_translations()

    def _(self, key, default=None):
        return self.translations.get(key, default if default is not None else key)
