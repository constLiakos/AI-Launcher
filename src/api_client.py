import requests
import json

class ApiClient:
    def __init__(self, config):
        self.config = config
        self.current_request = None  # Track current request for cancellation

    def send_streaming_request(self, prompt):
        """Send a streaming request to the OpenAI compatible API."""
        try:
            api_key = self.config.get('api_key')
            api_base = self.config.get('api_base')
            model = self.config.get('model')

            if not api_key:
                raise Exception("API key not configured. Please check settings.")

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.config.get('max_tokens', 500),
                "temperature": self.config.get('temperature', 0.7),
                "stream": True  # Enable streaming
            }

            # Make streaming request
            self.current_request = requests.post(
                f"{api_base}/chat/completions",
                headers=headers,
                data=json.dumps(data),
                timeout=30,
                stream=True  # Enable response streaming
            )

            if self.current_request.status_code != 200:
                error_info = self.current_request.json()
                error_message = error_info.get("error", {}).get("message", "Unknown API error")
                raise Exception(f"API Error: {error_message}")

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
                                    yield delta['content']
                                    
                        except json.JSONDecodeError:
                            # Skip malformed JSON chunks
                            continue

        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            raise Exception(f"Streaming request failed: {str(e)}")
        finally:
            self.current_request = None

    def cancel_request(self):
        """Cancel ongoing streaming request."""
        if self.current_request:
            try:
                self.current_request.close()
                self.current_request = None
            except:
                pass  # Ignore errors during cancellation