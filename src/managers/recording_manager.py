import logging
import sounddevice as sd
import threading
import wave
import os
import time
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication
from managers.state_manager import StateManager
from utils.constants import Directories, Files

class RecordingManager(QObject):
    # Qt signals for thread-safe communication
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    recording_failed = pyqtSignal(str)
    audio_saved = pyqtSignal(str)
    recording_progress = pyqtSignal(float)
    
    def __init__(self, state_manager, config, parent=None):
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.state_manager: StateManager = state_manager
        self.config = config
        self.tmp_dir = self.config.get('tmp_dir', Directories.DEFAULT_TMP)
        os.makedirs(self.tmp_dir, exist_ok=True)
        self.audio_file_path = str(Files.RECORDING_FILE_PATH)
        
        # Initialize audio recording attributes
        self.frames = []
        self.is_recording = False
        self.record_thread = None
        self.fs = 16000
        self._frames_lock = threading.Lock()
        self._stop_event = threading.Event()
        
        # Qt-specific attributes
        self._progress_timer = QTimer()
        self._progress_timer.timeout.connect(self._update_progress)
        self._recording_start_time = None
        
        # Connect signals to slots if needed
        self.recording_failed.connect(self._handle_recording_error)

    def toggle_recording(self):
        """Toggle speech-to-text recording - safe to call from GUI thread."""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start recording audio for speech-to-text."""
        self.logger.debug("Starting audio recording")
        self.is_recording = True
        self._recording_start_time = time.time()
        self._stop_event.clear()
        
        with self._frames_lock:
            self.frames = []
            
        self._progress_timer.start(500)
        
        self.record_thread = threading.Thread(target=self.record_audio, daemon=True)
        self.record_thread.start()
                
        self.recording_started.emit()
        return True

    def record_audio(self):
        """Record audio data - runs in separate thread."""
        try:
            self.logger.debug("Starting Recording input stream")
            
            # Check if audio devices are available
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            if not input_devices:
                raise RuntimeError("No audio input devices available")
                
            with sd.InputStream(
                samplerate=self.fs, 
                channels=1, 
                dtype='int16', 
                callback=self.audio_callback,
                blocksize=1024
            ):
                while not self._stop_event.wait(timeout=0.2):
                    if not self.is_recording:
                        break
                    
            self.logger.debug("Recording completed")
            self.recording_completed()
            
            # Save audio after recording stops
            with self._frames_lock:
                frames_count = len(self.frames)
                
            if frames_count > 0:
                self.save_audio()
            else:
                self.logger.warning("No audio data recorded")
                self.recording_failed.emit("No audio data recorded")
                
        except (sd.PortAudioError, RuntimeError) as e:
            error_msg = f"Audio device error: {e}"
            self.logger.error(error_msg)
            self.recording_failed.emit(error_msg)
            
        except Exception as e:
            error_msg = f"Recording failed: {e}"
            self.logger.error(error_msg)
            self.recording_failed.emit(error_msg)
            
        finally:
            self.is_recording = False
            self._progress_timer.stop()

    def audio_callback(self, indata, frames, time_, status):
        """Audio input callback - runs in audio thread."""
        if status:
            self.logger.warning(f"InputStream status: {status}")
            
        if self.is_recording:
            try:
                with self._frames_lock:
                    self.frames.append(indata.tobytes())
            except Exception as e:
                self.logger.error(f"Error in audio callback: {e}")

    def stop_recording(self):
        """Stop recording - safe to call from GUI thread."""        
        self.logger.debug("Stopping audio recording")
        self.is_recording = False
        self._stop_event.set()
        self._progress_timer.stop()
        
        # Wait for the recording thread to finish
        if self.record_thread and self.record_thread.is_alive():
            self.record_thread.join(timeout=5.0)
            if self.record_thread.is_alive():
                self.logger.warning("Recording thread did not stop gracefully")

        self.recording_stopped.emit()

    def save_audio(self):
        """Save recorded audio frames to file."""
        try:
            os.makedirs(os.path.dirname(self.audio_file_path), exist_ok=True)
            
            with self._frames_lock:
                audio_data_bytes = b''.join(self.frames)
            
            with wave.open(self.audio_file_path, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.fs)
                wav_file.writeframes(audio_data_bytes)
                
            self.logger.debug(f"Audio saved to {self.audio_file_path}")
            self.audio_saved.emit(self.audio_file_path)
            
        except Exception as e:
            error_msg = f"Failed to save audio: {e}"
            self.logger.error(error_msg)
            self.recording_failed.emit(error_msg)

    def _update_progress(self):
        """Update recording progress - runs in main thread."""
        if self.is_recording and self._recording_start_time:
            duration = time.time() - self._recording_start_time
            self.recording_progress.emit(duration)

    def _handle_recording_error(self, error_message):
        """Handle recording errors - runs in main thread."""
        self.logger.error(f"Recording error handled: {error_message}")
        if hasattr(self.state_manager, 'stt_recording_failed'):
            self.stt_recording_failed()

    def cleanup(self):
        """Clean up resources - call this when closing the application."""
        if self.is_recording:
            self.stop_recording()
        
        self._progress_timer.stop()
        
        if os.path.exists(self.audio_file_path):
            try:
                os.remove(self.audio_file_path)
                self.logger.debug("Temporary audio file cleaned up")
            except Exception as e:
                self.logger.warning(f"Failed to clean up audio file: {e}")

    def get_recording_state(self):
        """Get current recording state - thread-safe."""
        return self.is_recording

    def get_audio_devices(self):
        """Get available audio input devices."""
        try:
            devices = sd.query_devices()
            input_devices = []
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    input_devices.append({
                        'index': i,
                        'name': device['name'],
                        'channels': device['max_input_channels']
                    })
            return input_devices
        except Exception as e:
            self.logger.error(f"Failed to get audio devices: {e}")
            return []

    
    def stt_recording_failed(self):
        """Stop speech-to-text recording."""
        # self.stt_state_changed.emit("idle")
        self.recording_failed.emit()
        return True

    def get_stt_state(self):
        """Get STT State"""
        return self.is_recording
    
    def recording_completed(self):
        self.recording_stopped.emit()