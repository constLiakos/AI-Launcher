import requests
import json
import os # Used for os.path.basename

class SttApiClient:
    def __init__(self, config):
        """
        Initializes the STT API client.
        Args:
            config (dict): A dictionary containing STT configuration.
                           Expected keys: 'stt_api_base', 'stt_api_key', 
                                          'stt_model', 'stt_request_timeout'.
        """
        self.api_base_url = config.get('stt_api_base')
        self.api_token = config.get('stt_api_key')
        self.model_name = config.get('stt_model')
        self.timeout = config.get('stt_request_timeout', 30) # Default timeout 30s

        if not self.api_base_url or not self.api_token or not self.model_name:
            raise ValueError("STT API base URL, token, and model name must be configured.")

    def transcribe(self, audio_file_path):
        """
        Transcribes the given audio file using the STT API.
        Args:
            audio_file_path (str): The path to the audio file to transcribe.
        Returns:
            str: The transcribed text.
        Raises:
            FileNotFoundError: If the audio file does not exist.
            requests.exceptions.RequestException: For network or request-related errors.
            Exception: For API errors or other issues during transcription.
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        try:
            with open(audio_file_path, 'rb') as f:
                files = {
                    # Use the actual filename for the form data
                    'file': (os.path.basename(audio_file_path), f, 'audio/wav') 
                }
                headers = {
                    'Authorization': f'Bearer {self.api_token}'
                }
                # Ensure the URL is correctly formed, typically ending with /v1/audio/transcriptions
                url = f"{self.api_base_url.rstrip('/')}/v1/audio/transcriptions"
                data = {
                    "model": self.model_name
                }

                response = requests.post(
                    url, 
                    headers=headers, 
                    files=files, 
                    data=data, 
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    try:
                        json_resp = response.json()
                        text = json_resp.get('text', '')
                        return text
                    except json.JSONDecodeError as e:
                        raise Exception(f"Failed to decode JSON response: {str(e)}. Response content: {response.text}")
                else:
                    try:
                        err_details = response.json()
                    except json.JSONDecodeError:
                        err_details = response.text
                    raise Exception(f"STT API Error: Status {response.status_code}, Details: {err_details}")
        
        except requests.exceptions.RequestException as e:
            # Re-raise requests exceptions to allow for specific handling if needed
            raise Exception(f"Network or request error during STT: {str(e)}")
        except Exception as e:
            # Catch any other exceptions and wrap them
            raise Exception(f"STT transcription failed: {str(e)}")
