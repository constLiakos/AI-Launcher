from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from streaming_worker import StreamingWorker
from utils.constants import Timing


class StateManager(QObject):
    """Manages application state and coordinates between UI and API operations."""

    # Signals for state changes
    state_changed = pyqtSignal(str)  # 'normal', 'thinking',  'error'
    processing_changed = pyqtSignal(bool)
    response_ready = pyqtSignal(str)
    request_cancelled = pyqtSignal()
    request_ready = pyqtSignal(str)
    expanded_changed = pyqtSignal(bool)

    def __init__(self, config):
        super().__init__()
        self.config = config

        # State tracking
        self.current_prompt = ""
        self.is_expanded = False
        self.response_visible = False
        self.is_processing = False
        self.current_request_id = 0
        self.accumulated_response = ""
        self.current_state = "normal"  # 'normal', 'typing', 'thinking', 'error'

        # Worker management
        self.streaming_worker = None

        # Debounced request timer
        self.request_timer = QTimer()
        self.request_timer.setSingleShot(True)
        self.request_timer.timeout.connect(self._send_request_signal)

        # Request delay from config
        delay_seconds = self.config.get(
            'request_delay', Timing.DEFAULT_REQUEST_DELAY_SECONDS)
        self.request_delay_ms = int(delay_seconds * 1000)

    def handle_first_chunk(self):
        """Handle first chunk reception - triggers UI expansion."""
        if not self.response_visible:
            self.show_response()
            return True  # Indicates this was the first chunk
        return False

    def set_prompt(self, prompt):
        """Update current prompt and handle state transitions."""
        self.current_prompt = prompt.strip()

        # Cancel any ongoing request when text changes significantly
        if self.is_processing:
            self.cancel_current_request()

        # Stop any pending timers
        self.request_timer.stop()

        if self.current_prompt:
            self.set_state("typing")
            self.request_timer.start(self.request_delay_ms)
        else:
            self.cleanup_state()

    def create_streaming_worker(self, api_client, request_id):
        """Create and configure streaming worker."""
        if not self.is_request_valid(request_id):
            return None

        # Create worker with current prompt
        worker = StreamingWorker(api_client, self.current_prompt, request_id)
        self.streaming_worker = worker
        return worker

    def handle_completion(self, request_id):
        """Handle successful completion of request."""
        if not self.is_request_valid(request_id):
            return False

        self.stop_processing()
        return True

    def force_send_request(self):
        """Immediately send request (e.g., when Enter is pressed)."""
        if self.current_prompt.strip():
            self.request_timer.stop()
            self._send_request_signal()

    def set_state(self, new_state):
        """Set application state and emit signal if changed."""
        if self.current_state != new_state:
            self.current_state = new_state
            self.state_changed.emit(new_state)

    def start_processing(self):
        """Mark request as processing and update state."""
        self.current_request_id += 1
        self.is_processing = True
        self.accumulated_response = ""
        self.set_state("thinking")
        self.processing_changed.emit(True)
        return self.current_request_id

    def stop_processing(self):
        """Mark processing as complete and update state."""
        self.is_processing = False
        self.set_state("normal")
        self.processing_changed.emit(False)

    def cancel_current_request(self):
        """Cancel current request and cleanup state."""
        if not self.is_processing:
            return

        # Increment request ID to invalidate current request
        self.current_request_id += 1
        self.is_processing = False

        # FIXED: Clear accumulated response when cancelling
        self.accumulated_response = ""

        # Cleanup worker
        if self.streaming_worker and self.streaming_worker.isRunning():
            self.streaming_worker.stop()
            # Don't wait too long for cleanup
            QTimer.singleShot(100, self._cleanup_worker)

        # Reset state
        self.set_state("normal")
        self.processing_changed.emit(False)
        self.request_cancelled.emit()

    def cleanup_state(self):
        """Clean up state when input is cleared."""
        # FIXED: Hide response first, then set state
        if self.response_visible:
            self.hide_response()

        if self.is_processing:
            self.cancel_current_request()

        # Set state to normal after cleanup
        self.set_state("normal")

    def show_response(self):
        """Mark response as visible and expanded."""
        if not self.is_expanded:  # Only emit if state actually changes
            self.is_expanded = True
            self.expanded_changed.emit(True)
        self.response_visible = True

    def hide_response(self):
        """Mark response as hidden and contracted."""
        if self.is_expanded:  # Only emit if state actually changes
            self.is_expanded = False
            self.expanded_changed.emit(False)
        self.response_visible = False

    def add_response_chunk(self, chunk):
        """Add chunk to accumulated response."""
        self.accumulated_response += chunk

    def get_accumulated_response(self):
        """Get the complete accumulated response."""
        return self.accumulated_response

    def is_request_valid(self, request_id):
        """Check if request ID is still valid."""
        return request_id == self.current_request_id and self.is_processing

    def handle_error(self, error_message, request_id=None):
        """Handle error state with optional request validation."""
        if request_id and not self.is_request_valid(request_id):
            return False

        self.is_processing = False
        error_text = f"❌ Error: {error_message}"
        self.accumulated_response = error_text
        self.set_state("error")
        self.processing_changed.emit(False)

        # Ensure response is visible for error display
        if not self.response_visible:
            self.show_response()

        return True

    def update_request_delay(self):
        """Update request delay from config."""
        delay_seconds = self.config.get('request_delay', 1.5)
        self.request_delay_ms = int(delay_seconds * 1000)

    def _send_request_signal(self):
        """Internal method to emit request signal."""
        self.set_state("thinking")
        if self.current_prompt.strip():
            self.request_ready.emit(self.current_prompt)

    def cleanup_worker_safely(self):
        """Safely cleanup the current worker."""
        if self.streaming_worker:
            self.streaming_worker.deleteLater()
            self.streaming_worker = None

    def _cleanup_worker(self):
        """Cleanup worker thread safely."""
        if self.streaming_worker:
            if self.streaming_worker.isRunning():
                self.streaming_worker.terminate()
            self.streaming_worker = None

    # Getters for current state
    def get_current_prompt(self):
        return self.current_prompt

    def get_current_state(self):
        return self.current_state

    def get_request_id(self):
        return self.current_request_id

    def is_currently_processing(self):
        return self.is_processing

    def is_currently_expanded(self):
        return self.is_expanded

    def is_response_currently_visible(self):
        return self.response_visible
