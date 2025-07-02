import requests
import json
import os

class OllamaClient:
    def __init__(
            self,
            use_history=False,
            api_url="http://localhost:11434/api/chat",
            model="mistral:latest"
    ):
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

class OpenAIClient:
    def __init__(
            self,
            api_key=None,
            use_history=False,
            api_url="https://api.openai.com/v1/chat/completions",
            model="gpt-4o"
    ):
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key is None:
                raise ValueError("API key not provided and OPENAI_API_KEY environment variable not set.")

        self.api_url = api_url
        self.model = model
        self.api_key = api_key
        self.history = []
        self.use_history = use_history
        self.embedding_url = "https://api.openai.com/v1/embeddings"
        self._check_model_exists()

    def _check_model_exists(self):
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get("https://api.openai.com/v1/models", headers=headers)
            if response.status_code == 200:
                models = response.json().get("data", [])
                if not any(m["id"] == self.model for m in models):
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
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
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
            response = requests.post(self.api_url, json=payload, headers=headers, stream=True)
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            line_data = line.decode('utf-8')
                            if line_data.startswith("data: "):
                                line_data = line_data[6:]
                                if line_data.strip() == "[DONE]":
                                    break
                                response_data = json.loads(line_data)
                                content = self.parse_response(response_data)
                                if content:
                                    full_response += content
                                    print(content, end='', flush=True)
                        except json.JSONDecodeError:
                            continue
                print()
                if self.use_history:
                    self.history.append({"role": "assistant", "content": full_response})
                return full_response
            else:
                raise Exception(f"OpenAI API request failed with status {response.status_code}")
        else:
            response = requests.post(self.api_url, json=payload, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                assistant_response = self.parse_response(response_data)
                if self.use_history:
                    self.history.append({"role": "assistant", "content": assistant_response})
                return assistant_response
            else:
                raise Exception(f"OpenAI API request failed with status {response.status_code}")

    def parse_response(self, response_data):
        if "choices" in response_data and len(response_data["choices"]) > 0:
            choice = response_data["choices"][0]
            if "delta" in choice and "content" in choice["delta"]:
                return choice["delta"]["content"] or ""
            elif "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]
        return ""

    def get_embedding(self, text, model="text-embedding-3-small"):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"input": text, "model": model}
        response = requests.post(self.embedding_url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()["data"][0]["embedding"]
        else:
            raise Exception(f"OpenAI Embedding API request failed with status {response.status_code}")

