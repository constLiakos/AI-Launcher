import logging
import sounddevice as sd
import threading
import numpy as np
import wavio
import os

from managers.state_manager import StateManager
from utils.constants import Directories, Files


class Recording_Manager:
    def __init__(self, logger: logging.Logger, state_manager, config):
        self.logger = logger.getChild('recording_manager')  # Fixed logger name
        self.state_manager: StateManager = state_manager
        self.config = config

        self.tmp_dir = self.config.get('tmp_dir', Directories.DEFAULT_TMP)
        os.makedirs(self.tmp_dir, exist_ok=True)

        self.audio_file_path = str(Files.RECORDING_FILE_PATH)
        
        # Initialize audio recording attributes
        self.frames = []
        self.recording = False
        self.record_thread = None
        self.fs = 16000  # Sample rate

    # Recording
    def toggle_recording(self):
        """Toggle speech-to-text recording."""
        current_state = self.state_manager.get_stt_state()
        self.logger.debug(f"Current State is: {current_state}")
        if current_state == "idle":
            self.start_recording()
        elif current_state == "recording":
            self.stop_recording()

    def start_recording(self):
        """Start recording audio for speech-to-text."""
        if not self.state_manager.stt_start_recording():
            self.logger.debug("Start recording did not start as expected")
            return
        
        self.logger.debug("Starting audio recording")
        self.recording = True
        self.frames = []
        self.record_thread = threading.Thread(target=self.record_audio, daemon=True)
        self.record_thread.start()
        self.logger.debug("Recording started")

    def record_audio(self):
        """Record audio data."""
        try:
            self.logger.debug("Starting Recording input stream")
            with sd.InputStream(samplerate=self.fs, channels=1, dtype='int16', callback=self.audio_callback):
                while self.recording:
                    sd.sleep(100)

            self.logger.debug("Recording completed")
            self.state_manager.recording_completed()

            # Save audio after recording stops
            if len(self.frames) > 0:
                self.save_audio()
            else:
                self.logger.warning("No audio data recorded")
                
        except Exception as e:
            self.logger.error(f"Recording failed: {e}")
        finally:
            self.recording = False

    def audio_callback(self, indata, frames, time_, status):
        """Audio input callback."""
        if status:
            self.logger.warning(f"InputStream status: {status}")
        if self.recording:  # Only append if we're actively recording
            self.frames.append(indata.copy().tobytes())

    def stop_recording(self):
        """Stop recording and process speech-to-text."""
        if not self.state_manager.stt_stop_recording():
            return
        
        self.logger.debug("Stopping audio recording")
        self.recording = False
        
        # Wait for the recording thread to finish
        if self.record_thread and self.record_thread.is_alive():
            self.record_thread.join(timeout=2.0)  # Wait max 2 seconds
            if self.record_thread.is_alive():
                self.logger.warning("Recording thread did not stop gracefully")

    def save_audio(self):
        """Save recorded audio frames to file."""
        try:
            # Ensure directory exists before saving
            os.makedirs(os.path.dirname(self.audio_file_path), exist_ok=True)
            
            audio_data_bytes = b''.join(self.frames)
            data_np = np.frombuffer(audio_data_bytes, dtype='int16')
            wavio.write(self.audio_file_path, data_np, self.fs, sampwidth=2)
            self.logger.debug(f"Audio saved to {self.audio_file_path}")
        except Exception as e:
            self.logger.error(f"Failed to save audio: {e}")