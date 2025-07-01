import requests
import json

class OllamaClient:
    def __init__(self, use_history=False, api_url="http://localhost:11434/api/chat", model="mistral:latest"):
        self.api_url = api_url
        self.model = model
        self.history = []
        self.use_history = use_history
        self._check_model_exists()

    def _check_model_exists(self):
        try:
            response = requests.get(f"{self.api_url.replace('/chat', '/tags')}")
            if response.status_code == 200:
                models = response.json().get("models", [])
                if not any(m["name"] == self.model for m in models):
                    raise ValueError(f"Model '{self.model}' not found")
            else:
                raise Exception(f"Failed to fetch models: {response.status_code}")
        except requests.RequestException as e:
            raise Exception(f"Error checking model: {str(e)}")

    def enable_history(self):
        self.use_history = True

    def disable_history(self):
        self.use_history = False
        self.history = []

    def request(self, prompt, stream=False):
        if self.use_history:
            self.history.append({"role": "user", "content": prompt})
            payload = {
                "model": self.model,
                "messages": self.history,
                "stream": stream
            }
        else:
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": stream
            }

        if stream:
            response = requests.post(self.api_url, json=payload, stream=True)
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            response_data = json.loads(line.decode('utf-8'))
                            content = self.parse_response(response_data)
                            full_response += content
                            print(content, end='', flush=True)
                        except json.JSONDecodeError:
                            continue
                print()
                if self.use_history:
                    self.history.append({"role": "assistant", "content": full_response})
                return full_response
            else:
                raise Exception(f"Ollama API request failed with status {response.status_code}")
        else:
            response = requests.post(self.api_url, json=payload)
            if response.status_code == 200:
                response_data = response.json()
                assistant_response = self.parse_response(response_data)
                if self.use_history:
                    self.history.append({"role": "assistant", "content": assistant_response})
                return assistant_response
            else:
                raise Exception(f"Ollama API request failed with status {response.status_code}")

    def parse_response(self, response_data):
        if "message" in response_data and "content" in response_data["message"]:
            return response_data["message"]["content"]
        else:
            raise ValueError("Invalid response format: 'message' or 'content' key not found")

