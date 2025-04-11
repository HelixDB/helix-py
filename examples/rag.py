import helix
#from helix.loader import hnswload,

import requests

def query_llama(prompt, model="llama3.1"):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            # Parse the JSON response
            result = response.json()
            return result.get("response", "No response generated")
        else:
            return f"Error: Request failed with status code {response.status_code}"

    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Make sure it's running locally."
    except Exception as e:
        return f"Error: An unexpected error occurred: {str(e)}"

if __name__ == "__main__":



    prompt = "What is the capital of France?"
    response = query_llama(prompt)

    print("Prompt:", prompt)
    print("Response:", response)
