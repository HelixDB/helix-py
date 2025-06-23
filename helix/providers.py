import requests
#import json

class OllamaClient:
    def __init__(self, api_url="http://localhost:11434/api/generate", model="mistral:latest"):
        self.api_url = api_url
        self.model = model
        self._check_model_exists()

    def _check_model_exists(self):
        try:
            response = requests.get(f"{self.api_url.replace('/generate', '/tags')}")
            if response.status_code == 200:
                models = response.json().get("models", [])
                if not any(m["name"] == self.model for m in models):
                    raise ValueError(f"Model '{self.model}' not found")
            else:
                raise Exception(f"Failed to fetch models: {response.status_code}")
        except requests.RequestException as e:
            raise Exception(f"Error checking model: {str(e)}")

    def request(self, prompt, stream=False):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream
        }
        response = requests.post(self.api_url, json=payload)
        if response.status_code == 200:
            return self.parse_response(response.json())
        else:
            raise Exception(f"Ollama API request failed with status {response.status_code}")

    def parse_response(self, response_data):
        if "response" in response_data:
            return response_data["response"]
        else:
            raise ValueError("Invalid response format: 'response' key not found")

