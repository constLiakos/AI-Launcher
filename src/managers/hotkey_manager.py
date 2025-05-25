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
        self.logger.info("HotkeyManager initialized")
        
    def setup_hotkey(self):
        """Setup global hotkey from config."""
        # Stop existing listener if any
        self.stop_listener()
            
        def on_hotkey():
            self.logger.debug("Hotkey pressed, triggering callback")
            # Use QTimer to ensure callback runs in main thread
            QTimer.singleShot(0, self.callback)
        
        # Get hotkey from config
        hotkey_combo = self.config.get('hotkey', '<alt>+x')
        self.logger.info(f"Setting up hotkey: {hotkey_combo}")
        
        try:
            hotkey = keyboard.HotKey(
                keyboard.HotKey.parse(hotkey_combo),
                on_hotkey
            )
            
            def start_listener():
                self.logger.debug("Starting hotkey listener thread")
                self.current_listener = keyboard.Listener(
                    on_press=hotkey.press,
                    on_release=hotkey.release
                )
                self.current_listener.start()
                self.logger.info("Hotkey listener started successfully")
                self.current_listener.join()
            
            listener_thread = threading.Thread(target=start_listener, daemon=True)
            listener_thread.start()
            
        except Exception as e:
            self.logger.error(f"Invalid hotkey format: {hotkey_combo}. Error: {e}. Using default.")
            # Fallback to default hotkey
            self.config.set('hotkey', '<alt>+x')
            self.setup_hotkey()  # Retry with default

    def stop_listener(self):
        """Stop the current hotkey listener."""
        if self.current_listener:
            self.logger.debug("Stopping hotkey listener")
            try:
                self.current_listener.stop()
                self.logger.info("Hotkey listener stopped successfully")
            except Exception as e:
                self.logger.error(f"Error stopping hotkey listener: {e}")
            finally:
                self.current_listener = None
        else:
            self.logger.debug("No active listener to stop")

    def restart_listener(self):
        """Restart the hotkey listener with new settings."""
        self.logger.info("Restarting hotkey listener")
        self.setup_hotkey()

    def cleanup(self):
        """Clean up resources."""
        self.logger.info("Cleaning up HotkeyManager resources")
        self.stop_listener()