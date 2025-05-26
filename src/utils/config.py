import json
import os
from pathlib import Path

from utils.constants import LLM, Conversation, Hotkey, Theme, Timing, WindowSize

class Config:
    def __init__(self):
        self.config_path = os.path.join(str(Path.home()), '.config', 'ai_launcher', 'config.json')
        self.default_config = {
            'api_key': '',
            'api_base': LLM.DEFAULT_API_BASE,
            'model': LLM.DEFAULT_LLM_MODEL,
            'window_width': WindowSize.COMPACT_WIDTH,
            'window_height': WindowSize.COMPACT_HEIGHT,
            'position_x': WindowSize.DEFAULT_X,
            'position_y': WindowSize.DEFAULT_Y,
            'request_delay': Timing.DEFAULT_REQUEST_DELAY_SECONDS,
            'hotkey': Hotkey.DEFAULT_HOTKEY_TOGGLE_MINIMIZE_WINDOW,
            'theme': Theme.DEFAULT_THEME,
            'message_history_limit': Conversation.DEFAULT_CONVERSATION_HISTORY_LIMIT,
            'clear_last_response_on_minimize': Conversation.DEFAULT_CLEAR_LAST_RESPONSE_ON_MINIMIZE,
            'clear_history_on_minimize': Conversation.DEFAULT_CLEAR_HISTORY_ON_MINIMIZE,
        }
        self.config = self.load_config()

    def load_config(self):
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                self.save_config(self.default_config)
                return self.default_config
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            return self.default_config

    def save_config(self, config):
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            self.config = config
        except Exception as e:
            print(f"Error saving config: {str(e)}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config(self.config)