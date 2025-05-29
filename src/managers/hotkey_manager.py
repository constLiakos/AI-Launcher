import logging
from pynput.keyboard import Controller, Listener, HotKey
import threading
from PyQt5.QtCore import pyqtSignal, QObject

from utils.constants import Hotkey
import time

class HotkeyManager(QObject):

    hotkey_pressed = pyqtSignal()

    def __init__(self, logger: logging.Logger, callback, config):
        """
        Initialize hotkey manager.
        Args:
            callback: Function to call when hotkey is pressed
            config: Configuration object to get hotkey settings
        """
        super().__init__()
        self.logger = logger.getChild('hotkey_manager')

        self.logger.debug("HotkeyManager initializing...")
        self.callback = callback
        self.config = config
        self.current_listener = None
        self.controller = Controller()

        # Connect signal to callback for thread safety
        self.hotkey_pressed.connect(callback)

        self.logger.info("HotkeyManager initialized")
        
    def setup_hotkey(self):
        """Setup global hotkey from config."""
        # Stop existing listener if any
        self.stop_listener()
            
        def on_hotkey():
            self.logger.debug("Hotkey pressed, emitting signal")
            # Emit signal instead of direct callback - safer on Windows
            self.hotkey_pressed.emit()
        
        # Get hotkey from config
        hotkey_combo = self.config.get('hotkey', Hotkey.DEFAULT_HOTKEY_TOGGLE_MINIMIZE_WINDOW)
        self.logger.info(f"Setting up hotkey: {hotkey_combo}")
        
        try:
            hotkey = HotKey(
                HotKey.parse(hotkey_combo),
                on_activate=on_hotkey
            )
            
            def for_canonical(f):
                return lambda k: f(self.current_listener.canonical(k))
            
            def start_listener():
                self.logger.debug("Starting hotkey listener thread")
                self.current_listener = Listener(
                    on_press=for_canonical(hotkey.press),
                    on_release=for_canonical(hotkey.release)
                )
                self.current_listener.start()
                self.logger.info("Hotkey listener started successfully")
                self.current_listener.join()
            
            listener_thread = threading.Thread(target=start_listener, daemon=True)
            listener_thread.start()
            
        except Exception as e:
            self.logger.error(f"Invalid hotkey format: {hotkey_combo}. Error: {e}. Using default.")
            # Fallback to default hotkey
            self.config.set('hotkey', Hotkey.DEFAULT_HOTKEY_TOGGLE_MINIMIZE_WINDOW)
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
        self.stop_listener()
        
        # Small delay to ensure cleanup is complete
        time.sleep(2)
        
        self.setup_hotkey()

    def cleanup(self):
        """Clean up resources."""
        self.logger.info("Cleaning up HotkeyManager resources")
        self.stop_listener()