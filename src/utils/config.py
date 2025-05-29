import json
import os

from utils.constants import LLM, STT, Conversation, Directories, Hotkey, Theme, Timing, WindowSize

class Config:
    def __init__(self):
        self.config_path = Directories.CONFIG
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
            'system_prompt': LLM.DEFAULT_SYSTEM_PROMPT,
            'stt_api_base': STT.DEFAULT_API_BASE,
            'stt_model': STT.DEFAULT_MODEL,
            'stt_request_timeout': STT.DEFAULT_REQUEST_TIMEOUT,
            'stt_hotkey': STT.DEFAULT_HOTKEY,
            'stt_enabled': STT.DEFAULT_ENABLED,
            'tmp_dir': Directories.DEFAULT_TMP,
            'max_tokens': LLM.MAX_TOKENS,
            'temperature': LLM.TEMPERATURE
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