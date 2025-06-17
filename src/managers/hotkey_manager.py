import logging
from pynput.keyboard import Controller, Listener, HotKey
import threading
from PyQt5.QtCore import pyqtSignal, QObject

from utils.constants import Hotkey
import time

class HotkeyManager(QObject):

    hotkey_pressed = pyqtSignal()
    stt_hotkey_pressed = pyqtSignal()

    def __init__(self, config):
        """
        Initialize hotkey manager.
        Args:
            callback: Function to call when hotkey is pressed
            config: Configuration object to get hotkey settings
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)

        self.logger.debug("HotkeyManager initializing...")
        self.config = config
        self.current_listener = None
        self.controller = Controller()

        self.logger.info("HotkeyManager initialized")

    def setup_hotkey(self):
        """Setup global hotkey from config."""
        self.logger.debug("Setting up hotkeys")
        # Stop existing listener if any
        self.stop_listener()
            
        def on_hotkey():
            self.logger.debug("Hotkey pressed, emitting signal")
            # Emit signal instead of direct callback - safer on Windows
            self.hotkey_pressed.emit()
        
        def on_stt_hotkey():
            self.logger.debug("STT hotkey pressed, emitting signal")
            self.stt_hotkey_pressed.emit()
        
        # Get hotkey from config
        hotkey_combo = self.config.get('hotkey', Hotkey.DEFAULT_HOTKEY_TOGGLE_MINIMIZE_WINDOW)
        stt_enabled = self.config.get('stt_enabled', False)

        self.logger.info(f"Setting up main hotkey: {hotkey_combo}")
        
        try:
            # Validate main hotkey first
            main_hotkey_keys = HotKey.parse(hotkey_combo)
            main_hotkey = HotKey(main_hotkey_keys, on_activate=on_hotkey)
            
        except Exception as e:
            self.logger.error(f"Invalid main hotkey format '{hotkey_combo}': {e}. Disabling main hotkey.")
            # Disable main hotkey by setting to None and return early
            self.config.set('hotkey', None)
            return
        
        # Create STT hotkey if STT is enabled
        stt_hotkey = None
        if stt_enabled:
            stt_hotkey_combo = self.config.get('stt_hotkey', 'ctrl+shift+v')
            self.logger.info(f"Setting up STT hotkey: {stt_hotkey_combo}")
            
            try:
                stt_hotkey_keys = HotKey.parse(stt_hotkey_combo)
                stt_hotkey = HotKey(stt_hotkey_keys, on_activate=on_stt_hotkey)
                
            except Exception as e:
                self.logger.error(f"Invalid STT hotkey format '{stt_hotkey_combo}': {e}. Disabling STT hotkey.")
                # Disable STT hotkey but continue with main hotkey
                self.config.set('stt_hotkey', None)
                stt_hotkey = None
        else:
            self.logger.info("STT disabled - skipping STT hotkey setup")

        try:
            def for_canonical(f):
                return lambda k: f(self.current_listener.canonical(k))
            
            def start_listener():
                self.logger.debug("Starting hotkey listener thread")

                if stt_hotkey:
                    # Handle both hotkeys
                    self.current_listener = Listener(
                        on_press=for_canonical(lambda k: (main_hotkey.press(k), stt_hotkey.press(k))),
                        on_release=for_canonical(lambda k: (main_hotkey.release(k), stt_hotkey.release(k)))
                    )
                else:
                    # Handle only main hotkey
                    self.current_listener = Listener(
                        on_press=for_canonical(main_hotkey.press),
                        on_release=for_canonical(main_hotkey.release)
                    )
                self.current_listener.start()
                self.logger.info("Hotkey listener started successfully")
                self.current_listener.join()
            
            listener_thread = threading.Thread(target=start_listener, daemon=True)
            listener_thread.start()

            self.logger.debug("Set up hotkeys copmleted")
        except Exception as e:
            self.logger.error(f"Failed to start hotkey listener: {e}. Hotkeys disabled.")
            self.current_listener = None

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
