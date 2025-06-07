import requests
import json

def send_mcp_request(method: str, params: dict, request_id: int) -> dict:
    payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": request_id}
    try:
        response = requests.post("http://localhost:6970/mcp", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

result = send_mcp_request("init", {"connection_addr": "localhost", "connection_port": 6969}, 1)
print(json.dumps(result, indent=2))

