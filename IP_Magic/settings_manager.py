import json
import os

SETTINGS_FILE = 'settings.json'


def load_settings():
    "加载用户设置"
    default_settings = {
        'auto_copy': False
    }
    
    if not os.path.exists(SETTINGS_FILE):
        return default_settings
    
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
        # 合并默认设置（处理新增的设置项）
        for key, value in default_settings.items():
            if key not in settings:
                settings[key] = value
        return settings
    except:
        return default_settings


def save_settings(settings):
    "保存用户设置"
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except:
        return False