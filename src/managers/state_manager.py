import logging
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from utils.streaming_worker import StreamingWorker
from utils.constants import Timing


class StateManager(QObject):
    """Manages application state and coordinates between UI and API operations (processing, expanded, etc.)"""

    # Signals for state changes
    processing_changed = pyqtSignal(bool)
    request_cancelled = pyqtSignal()
    request_ready = pyqtSignal(str)
    stt_state_changed = pyqtSignal(str)
    recording_completed_sg = pyqtSignal()
    clear_multiline_input_sg = pyqtSignal()

    def __init__(self, config, logger:logging.Logger):
        super().__init__()
        self.logger = logger.getChild('state_manager')
        self.config = config

        self.current_prompt = ""
        self.is_processing = False
        self.current_request_id = 0
        self.accumulated_response = ""
        self.streaming_worker = None

        # Debounced request timer
        self.request_timer = QTimer()
        self.request_timer.setSingleShot(True)
        self.request_timer.timeout.connect(self._send_request_signal)

        # Request delay from config
        delay_seconds = self.config.get(
            'request_delay', Timing.DEFAULT_REQUEST_DELAY_SECONDS)
        self.request_delay_ms = int(delay_seconds * 1000)
        
        # STT States
        self.stt_state = "idle"
        self.is_recording = False

        self.logger.debug(f"StateManager initialized with request delay: {self.request_delay_ms}ms")


    def handle_first_chunk(self):
        """Handle first chunk reception - triggers UI expansion."""
        self.logger.debug(f"Handling first chunk, response_visible: {self.response_visible}")
        if not self.response_visible:
            self.show_response()
            self.logger.debug("First chunk triggered UI expansion")
            return True  # Indicates this was the first chunk
        return False

    def set_prompt(self, prompt, is_multiline_input=False):
        """
        Update current prompt and handle state transitions.
        This stays in StateManager because it:
        1. Manages application logic (request timing, cancellation)
        2. Triggers business rules (auto-send vs manual send)
        3. Coordinates multiple state changes
        """
        old_prompt = self.current_prompt
        self.current_prompt = prompt.strip()
        self.logger.debug(f"Prompt changed from '{old_prompt[:50]}...' to '{self.current_prompt[:50]}...'")
        # Cancel any ongoing request when text changes significantly
        if self.is_processing and old_prompt != self.current_prompt:
            self.logger.debug("Cancelling current request due to prompt change")
            self.cancel_current_request()
        # Stop any pending timers
        self.request_timer.stop()
        if self.current_prompt:
            if not is_multiline_input:
                self.request_timer.start(self.request_delay_ms)
                self.logger.debug(f"Started auto-send timer for {self.request_delay_ms}ms")
        else:
            self.logger.debug("Empty prompt, cleaning up state")
            self.cleanup_state()

    def create_streaming_worker(self, api_client, request_id, conversation_history=None):
        """
        Create and configure streaming worker with optional conversation history.
        1. Manages worker lifecycle (self.streaming_worker)
        2. Validates request state (is_request_valid)
        3. Has access to current prompt and application state
        """
        self.logger.debug(f"Creating streaming worker for request_id: {request_id}")
        
        # Validate request is still current
        if not self.is_request_valid(request_id):
            self.logger.debug(f"Request {request_id} is invalid, not creating worker")
            return None
        
        # Ensure we have a prompt to work with
        if not self.current_prompt.strip():
            self.logger.debug("No prompt available, not creating worker")
            return None
        try:
            # Create worker with current application state
            worker = StreamingWorker(
                api_client=api_client,
                prompt=self.current_prompt,
                request_id=request_id,
                conversation_history=conversation_history
            )
            # Store reference for lifecycle management
            self.streaming_worker = worker
            self.logger.debug(f"Streaming worker created successfully for request {request_id}")
            return worker
        except Exception as e:
            self.logger.error(f"Failed to create streaming worker: {e}")
            return None

    def handle_completion(self, request_id):
        """Handle successful completion of request."""
        self.logger.debug(f"Handling completion for request_id: {request_id}")
        
        if not self.is_request_valid(request_id):
            self.logger.debug(f"Request {request_id} is invalid, ignoring completion")
            return False
        
        # Stop processing (application logic only)
        self.stop_processing()
        
        self.logger.debug(f"Request {request_id} completed successfully")
        return True

    def force_send_request(self):
        """Immediately send request (e.g., when Enter/Ctrl+Enter is pressed)."""
        self.logger.debug("Force sending request")
        if self.current_prompt.strip():
            self.request_timer.stop()
            self._send_request_signal()
        else:
            self.logger.debug("Cannot force send - no prompt available")


    def start_processing(self):
        """
        Mark request as processing and return new request ID.
        Only handles application logic - no UI state changes.
        """
        self.current_request_id += 1
        self.is_processing = True
        self.accumulated_response = ""
        
        self.logger.debug(f"Started processing request {self.current_request_id}")
        
        # Emit signal for application logic listeners (like settings button disable)
        self.processing_changed.emit(True)
        
        return self.current_request_id

    def stop_processing(self):
        """
        Mark processing as complete.
        Only handles application logic - no UI state changes.
        """
        self.logger.debug(f"Stopping processing for request {self.current_request_id}")
        
        self.is_processing = False
        
        # Emit signal for application logic listeners (like settings button enable)
        self.processing_changed.emit(False)

    def cancel_current_request(self):
        """
        Cancel current request and cleanup application state.
        Only handles application logic - no UI state changes.
        """
        if not self.is_processing:
            self.logger.debug("No request to cancel")
            return
        old_request_id = self.current_request_id
        # Increment request ID to invalidate current request
        self.current_request_id += 1
        self.is_processing = False
        self.logger.debug(f"Cancelled request {old_request_id}, new request_id: {self.current_request_id}")
        # Clear accumulated response when cancelling
        self.accumulated_response = ""
        # Cleanup worker
        if self.streaming_worker and self.streaming_worker.isRunning():
            self.logger.debug("Stopping streaming worker")
            self.streaming_worker.stop()
            # Don't wait too long for cleanup
            QTimer.singleShot(100, self._cleanup_worker)
        self.processing_changed.emit(False)
        self.request_cancelled.emit()

    def cleanup_state(self):
        """
        Clean up application state when input is cleared.
        Only handles application logic - no UI state changes.
        """
        self.logger.debug(f"Cleaning up state - is_processing: {self.is_processing}")
        
        # 1. Cancel any ongoing processing
        if self.is_processing:
            self.logger.debug("Cancelling current request during cleanup")
            self.cancel_current_request()
        
        # 2. Stop any pending auto-send timers
        if self.request_timer.isActive():
            self.request_timer.stop()
            self.logger.debug("Stopped pending request timer during cleanup")
        
        # 3. Clear accumulated response data
        if self.accumulated_response:
            self.accumulated_response = ""
            self.logger.debug("Cleared accumulated response during cleanup")
        
        # 4. Reset prompt (should already be empty, but ensure consistency)
        self.current_prompt = ""
        
        # 5. Clean up any active worker
        if self.streaming_worker:
            self.logger.debug("Cleaning up streaming worker during state cleanup")
            self.cleanup_worker_safely()
        
        # 6. Signal UI components that need to reset (like multiline input height)
        self.clear_multiline_input_sg.emit()
        
        self.logger.debug("State cleanup completed")

   

    def add_response_chunk(self, chunk):
        """Add chunk to accumulated response."""
        chunk_length = len(chunk)
        total_length = len(self.accumulated_response) + chunk_length
        self.accumulated_response += chunk
        self.logger.debug(f"Added chunk ({chunk_length} chars), total response: {total_length} chars")

    def get_accumulated_response(self):
        """Get the complete accumulated response."""
        return self.accumulated_response

    def is_request_valid(self, request_id):
        """Check if request ID is still valid."""
        return request_id == self.current_request_id and self.is_processing

    def handle_error(self, error_message, request_id=None):
        """Handle error state with optional request validation."""
        self.logger.debug(f"Handling error: {error_message}, request_id: {request_id}")
        if request_id and not self.is_request_valid(request_id):
            self.logger.debug(f"Error for invalid request {request_id}, ignoring")
            return False
        self.is_processing = False
        error_text = f"❌ Error: {error_message}"
        self.accumulated_response = error_text
        
        # Emit application logic signal
        self.processing_changed.emit(False)
        
        return True
    def cleanup_worker_safely(self):
        """Safely cleanup the current worker."""
        if self.streaming_worker:
            self.logger.debug("Cleaning up streaming worker safely")
            if self.streaming_worker.isRunning():
                self.streaming_worker.stop()
            self.streaming_worker.deleteLater()
            self.streaming_worker = None

    # Getters for current state
    def get_current_prompt(self):
        return self.current_prompt


    def get_request_id(self):
        return self.current_request_id

    def is_currently_processing(self):
        return self.is_processing


    def stt_start_recording(self):
        """Start speech-to-text recording."""
        if self.stt_state != "idle":
            return False
        
        self.stt_state = "recording"
        self.is_recording = True
        self.stt_state_changed.emit("recording")
        return True
    
    def stt_stop_recording(self):
        """Stop speech-to-text recording."""
        if self.stt_state != "recording":
            return False
        
        self.stt_state = "idle"
        self.is_recording = False
        self.stt_state_changed.emit("idle")
        return True

    def get_stt_state(self):
        """Get STT State"""
        return self.stt_state
    
    def recording_completed(self):
        self.recording_completed_sg.emit()


    def _cleanup_worker(self):
        """Internal cleanup method for timer-based cleanup."""
        if self.streaming_worker:
            self.logger.debug("Cleaning up worker thread")
            if self.streaming_worker.isRunning():
                self.streaming_worker.terminate()
            self.streaming_worker = None


    def _send_request_signal(self):
        """Internal method to emit request signal."""
        self.logger.debug(f"Sending request signal for prompt: '{self.current_prompt[:50]}{'...' if len(self.current_prompt) > 50 else ''}'")
        if self.current_prompt.strip():
            self.request_ready.emit(self.current_prompt)