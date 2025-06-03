import requests
import json

from utils.constants import LLM

class ApiClient:
    def __init__(self, logger, config):
        self.logger = logger.getChild('api_client')
        self.config = config
        self.current_request = None
        self.logger.debug("ApiClient initialized")

    def send_streaming_request(self, messages):
        """Send a streaming request to the OpenAI compatible API."""
        self.logger.info("Starting streaming request")
        
        try:
            api_key = self.config.get('api_key')
            api_base = self.config.get('api_base')
            model = self.config.get('model')
            system_prompt = self.config.get('system_prompt', LLM.DEFAULT_SYSTEM_PROMPT)
            
            self.logger.debug(f"Using model: {model}, API base: {api_base}")
            
            if not api_key:
                self.logger.error("API key not configured")
                raise Exception("API key not configured. Please check settings.")

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            # Handle both old format (single prompt string) and new format (messages array)
            if isinstance(messages, str):
                self.logger.debug("Converting legacy string prompt to messages format")
                messages_data = [{"role": "user", "content": messages}]
            else:
                self.logger.debug(f"Using messages array with {len(messages)} messages")
                messages_data = messages

            # Add system prompt if provided and not already present
            if system_prompt and (not messages_data or messages_data[0].get("role") != "system"):
                self.logger.debug("Adding system prompt to messages")
                messages_data.insert(0, {"role": "system", "content": system_prompt})

            data = {
                "model": model,
                "messages": messages_data,
                "max_tokens": self.config.get('max_tokens', LLM.MAX_TOKENS),
                "temperature": self.config.get('temperature', LLM.TEMPERATURE),
                "stream": True
            }

            self.logger.debug(f"Request payload prepared with {len(messages_data)} messages")

            # Make streaming request
            self.logger.info("Sending streaming request to API")
            self.current_request = requests.post(
                f"{api_base}/chat/completions",
                headers=headers,
                data=json.dumps(data),
                timeout=LLM.DEFAULT_REQUEST_TIMEOUT,
                stream=True
            )

            self.logger.debug(f"Received response with status code: {self.current_request.status_code}")

            if self.current_request.status_code != 200:
                self.logger.error(f"API returned error status: {self.current_request.status_code}")
                error_info = self.current_request.json()
                error_message = error_info.get("error", {}).get("message", "Unknown API error")
                self.logger.error(f"API error message: {error_message}")
                raise Exception(f"API Error: {error_message}")

            self.logger.info("Processing streaming response")
            chunk_count = 0
            
            # Process streaming response
            for line in self.current_request.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    # Skip empty lines and comments
                    if not line.strip() or line.startswith('#'):
                        continue
                    
                    # Parse Server-Sent Events format
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove 'data: ' prefix
                        
                        # Check for end of stream
                        if data_str.strip() == '[DONE]':
                            self.logger.debug("Received end of stream marker")
                            break
                        
                        try:
                            # Parse JSON chunk
                            chunk = json.loads(data_str)
                            # Extract content from chunk
                            if ('choices' in chunk and
                                len(chunk['choices']) > 0 and
                                'delta' in chunk['choices'][0]):
                                delta = chunk['choices'][0]['delta']
                                if 'content' in delta:
                                    chunk_count += 1
                                    if chunk_count % 10 == 0:  # Log every 10th chunk to avoid spam
                                        self.logger.debug(f"Processed {chunk_count} content chunks")
                                    yield delta['content']
                        except json.JSONDecodeError as json_err:
                            self.logger.warning(f"Skipping malformed JSON chunk: {json_err}")
                            continue

            self.logger.info(f"Streaming completed successfully. Total chunks processed: {chunk_count}")

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Request timeout: {str(e)}")
            raise Exception(f"Request timeout: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {str(e)}")
            raise Exception(f"Connection error: {str(e)}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error: {str(e)}")
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            self.logger.error(f"Streaming request failed: {str(e)}")
            raise Exception(f"Streaming request failed: {str(e)}")
        finally:
            self.current_request = None
            self.logger.debug("Streaming request cleanup completed")

    def cancel_request(self):
        """Cancel ongoing streaming request."""
        if self.current_request:
            self.logger.info("Cancelling ongoing streaming request")
            try:
                self.current_request.close()
                self.current_request = None
                self.logger.debug("Request cancelled successfully")
            except Exception as e:
                self.logger.warning(f"Error during request cancellation: {str(e)}")
        else:
            self.logger.debug("No active request to cancel")

    def get_available_models(self):
        """Get list of available models from the API."""
        self.logger.info("Fetching available models")
        
        try:
            api_key = self.config.get('api_key')
            api_base = self.config.get('api_base')
            
            if not api_key:
                self.logger.error("API key not configured")
                raise Exception("API key not configured. Please check settings.")

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            self.logger.debug(f"Requesting models from: {api_base}/models")
            
            response = requests.get(
                f"{api_base}/models",
                headers=headers,
                timeout=LLM.DEFAULT_REQUEST_TIMEOUT
            )

            self.logger.debug(f"Models API response status: {response.status_code}")

            if response.status_code != 200:
                self.logger.error(f"Models API returned error status: {response.status_code}")
                error_info = response.json() if response.content else {}
                error_message = error_info.get("error", {}).get("message", "Unknown API error")
                self.logger.error(f"Models API error message: {error_message}")
                raise Exception(f"Models API Error: {error_message}")

            models_data = response.json()
            
            # Extract model IDs from the response
            if 'data' in models_data and isinstance(models_data['data'], list):
                model_ids = [model.get('id') for model in models_data['data'] if model.get('id')]
                self.logger.info(f"Retrieved {len(model_ids)} available models")
                return model_ids
            else:
                self.logger.warning("Unexpected models API response format")
                return []

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Models request timeout: {str(e)}")
            raise Exception(f"Models request timeout: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Models connection error: {str(e)}")
            raise Exception(f"Models connection error: {str(e)}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Models network error: {str(e)}")
            raise Exception(f"Models network error: {str(e)}")
        except Exception as e:
            self.logger.error(f"Failed to fetch available models: {str(e)}")
            raise Exception(f"Failed to fetch available models: {str(e)}")
