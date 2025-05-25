from PyQt5.QtCore import QThread, pyqtSignal

class StreamingWorker(QThread):
    """Worker thread for streaming API responses."""
    chunk_received = pyqtSignal(str)  # Signal for each chunk
    response_complete = pyqtSignal()  # Signal when response is complete
    error_occurred = pyqtSignal(str)  # Signal for errors

    def __init__(self, api_client, prompt, request_id, conversation_history=None):
        super().__init__()
        self.api_client = api_client
        self.prompt = prompt
        self.request_id = request_id
        self.conversation_history = conversation_history or []
        self.should_stop = False

    def run(self):
        """Execute the streaming request with conversation history."""
        try:
            # Build messages array with history + current prompt
            messages = self.conversation_history.copy()
            messages.append({
                "role": "user",
                "content": self.prompt
            })
            
            # Use streaming API call with messages
            for chunk in self.api_client.send_streaming_request(messages):
                if self.should_stop:
                    return
                # Extract text from chunk (adjust based on your API format)
                if isinstance(chunk, dict) and 'content' in chunk:
                    self.chunk_received.emit(chunk['content'])
                elif isinstance(chunk, str):
                    self.chunk_received.emit(chunk)
            
            self.response_complete.emit()
        except Exception as e:
            if not self.should_stop:
                self.error_occurred.emit(str(e))

    def stop(self):
        """Stop the streaming worker."""
        self.should_stop = True