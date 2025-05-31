from PyQt5.QtCore import QThread, pyqtSignal

class StreamingWorker(QThread):
    """Worker thread for streaming API responses."""
    chunk_received = pyqtSignal(str)  # Signal for each chunk
    response_complete = pyqtSignal()  # Signal when response is complete
    error_occurred = pyqtSignal(str)  # Signal for errors

    def __init__(self, logger, api_client, prompt, request_id, conversation_history=None):
        super().__init__()
        self.logger = logger.getChild('streaming_worker')
        self.api_client = api_client
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
            self.logger.debug(f"Final message content preview: {self.prompt[:100]}...")
            
            # Use streaming API call with messages
            self.logger.debug("Initiating streaming API call")
            chunk_count = 0
            total_content_length = 0
            
            for chunk in self.api_client.send_streaming_request(messages):
                if self.should_stop:
                    self.logger.info(f"Streaming stopped by user - Request ID: {self.request_id}")
                    return
                    
                chunk_count += 1
                self.logger.debug(f"Received chunk #{chunk_count} - Type: {type(chunk)}")
                
                # Extract text from chunk (adjust based on your API format)
                if isinstance(chunk, dict) and 'content' in chunk:
                    content = chunk['content']
                    content_length = len(content)
                    total_content_length += content_length
                    self.logger.debug(f"Chunk content length: {content_length} chars")
                    self.chunk_received.emit(content)
                elif isinstance(chunk, str):
                    content_length = len(chunk)
                    total_content_length += content_length
                    self.logger.debug(f"String chunk length: {content_length} chars")
                    self.chunk_received.emit(chunk)
                else:
                    self.logger.warning(f"Unexpected chunk format: {type(chunk)} - {chunk}")
            
            self.logger.info(f"Streaming complete - Request ID: {self.request_id}")
            self.logger.info(f"Total chunks received: {chunk_count}")
            self.logger.info(f"Total content length: {total_content_length} characters")
            self.response_complete.emit()
            
        except Exception as e:
            if not self.should_stop:
                self.logger.error(f"Streaming error - Request ID: {self.request_id}")
                self.logger.error(f"Error type: {type(e).__name__}")
                self.logger.error(f"Error message: {str(e)}")
                self.logger.error(f"Prompt that caused error: {self.prompt[:200]}...")
                self.logger.exception("Full exception traceback:")
                self.error_occurred.emit(str(e))
            else:
                self.logger.debug(f"Exception occurred after stop - ignoring: {str(e)}")

    def stop(self):
        """Stop the streaming worker."""
        self.logger.info(f"Stop requested - Request ID: {self.request_id}")
        self.should_stop = True