import logging
from pynput import keyboard
import threading
from PyQt5.QtCore import QTimer

class HotkeyManager:
    def __init__(self, callback, config, logger:logging):
        """
        Initialize hotkey manager.
        
        Args:
            callback: Function to call when hotkey is pressed
            config: Configuration object to get hotkey settings
        """
        self.logger = logger.getChild('hotkey_manager')
        self.callback = callback
        self.config = config
        self.current_listener = None
        
    def setup_hotkey(self):
        """Setup global hotkey from config."""
        # Stop existing listener if any
        self.stop_listener()
            
        def on_hotkey():
            # Use QTimer to ensure callback runs in main thread
            QTimer.singleShot(0, self.callback)
        
        # Get hotkey from config
        hotkey_combo = self.config.get('hotkey', '<alt>+x')
        
        try:
            hotkey = keyboard.HotKey(
                keyboard.HotKey.parse(hotkey_combo),
                on_hotkey
            )
            
            def start_listener():
                self.current_listener = keyboard.Listener(
                    on_press=hotkey.press,
                    on_release=hotkey.release
                )
                self.current_listener.start()
                self.current_listener.join()
            
            listener_thread = threading.Thread(target=start_listener, daemon=True)
            listener_thread.start()
            
        except Exception as e:
            print(f"Invalid hotkey format: {hotkey_combo}. Using default.")
            # Fallback to default hotkey
            self.config.set('hotkey', '<alt>+x')
            self.setup_hotkey()  # Retry with default

    def stop_listener(self):
        """Stop the current hotkey listener."""
        if self.current_listener:
            try:
                self.current_listener.stop()
            except Exception as e:
                print(f"Error stopping hotkey listener: {e}")
            finally:
                self.current_listener = None

    def restart_listener(self):
        """Restart the hotkey listener with new settings."""
        self.setup_hotkey()

    def cleanup(self):
        """Clean up resources."""
        self.stop_listener()