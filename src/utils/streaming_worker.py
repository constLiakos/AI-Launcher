import logging
from PyQt5.QtCore import QThread, pyqtSignal
from utils.api_client import ApiClient

class StreamingWorker(QThread):
    """Worker thread for streaming API responses."""
    chunk_received = pyqtSignal(str)  # Signal for each chunk
    response_complete = pyqtSignal()  # Signal when response is complete
    error_occurred = pyqtSignal(str)  # Signal for errors

    def __init__(self, api_client, prompt, request_id, conversation_history=None):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.api_client:ApiClient = api_client
        self.prompt = prompt
        self.request_id = request_id
        self.conversation_history = conversation_history or []
        self.should_stop = False
        
        self.logger.debug(f"StreamingWorker initialized - Request ID: {request_id}")
        self.logger.debug(f"Prompt length: {len(prompt)} characters")
        self.logger.debug(f"Conversation history length: {len(self.conversation_history)} messages")

    def run(self):
        """Execute the streaming request with conversation history."""
        self.logger.info(f"Starting streaming request - Request ID: {self.request_id}")
        
        try:
            # Build messages array with history + current prompt
            messages = self.conversation_history.copy()
            messages.append({
                "role": "user",
                "content": self.prompt
            })
            
            self.logger.debug(f"Built messages array with {len(messages)} total messages")
            
            # Check if stopped before starting API call
            if self.should_stop:
                self.logger.info(f"Stopped before API call - Request ID: {self.request_id}")
                return
                
            # Use streaming API call with messages
            self.logger.debug("Initiating streaming API call")
            chunk_count = 0
            total_content_length = 0
            
            for chunk in self.api_client.send_streaming_request(messages):
                if self.should_stop:
                    self.logger.info(f"Streaming stopped by user - Request ID: {self.request_id}")
                    break
                    
                chunk_count += 1
                
                if isinstance(chunk, dict) and 'content' in chunk:
                    content = chunk['content']
                    total_content_length += len(content)
                    self.chunk_received.emit(content)
                elif isinstance(chunk, str):
                    total_content_length += len(chunk)
                    self.chunk_received.emit(chunk)
            
            # Only emit completion if not stopped
            if not self.should_stop:
                self.logger.info(f"Streaming complete - Request ID: {self.request_id}")
                self.response_complete.emit()
            
        except Exception as e:
            if not self.should_stop:
                self.logger.error(f"Streaming error - Request ID: {self.request_id}")
                self.error_occurred.emit(str(e))

    def stop(self):
        """Stop the streaming worker."""
        self.logger.info(f"Stop requested - Request ID: {self.request_id}")
        self.should_stop = True