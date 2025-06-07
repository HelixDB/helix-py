# testing mcp server

from flask import Flask, request, jsonify, Response
from jsonrpcserver import method, Result, Success, Error, dispatch
import requests
import json
import helix

app = Flask(__name__)
client = helix.Client(local=True, port=6969)

@method
def init(**kwargs) -> Result:
    try:
        conn_addr = kwargs.get("connection_addr")
        conn_port = kwargs.get("connection_port")
        if not conn_addr or not isinstance(conn_port, int) or conn_port < 0 or conn_port > 65535:
            return Error(code=-32000, message="Invalid or missing connection_addr or connection_port")

        response = client.query(helix.init(str(conn_addr), conn_port)) # tmp for [0]
        return Success(response[0])

    except requests.RequestException as e:
        return Error(code=-32000, message=f"Invalid response from Helix: {e}")

@method
def call_tool(params: dict) -> Result:
    try:
        connection_id = params.get("connection_id")
        tool = params.get("tool")
        args = params.get("args", {})

        if not connection_id:
            return Error(code=-32602, message="Missing connection_id. Call init first.")
        if not tool:
            return Error(code=-32602, message="Missing tool parameter")

        payload = {
            "connection_id": connection_id,
            "tool": tool,
            "args": args,
        }
        response = client.query(helix.call_tool(payload))
        return Success(response[0])
    except requests.RequestException as e:
        return Error(code=-32000, message=f"Network error: {str(e)}")

@method
def next(params: dict) -> Result:
    try:
        conn_id = params.get("connection_id")
        if not conn_id:
            return Error(code=-32602, message="Missing connection_id. Call init first.")

        response = client.query(helix.next(conn_id))
        return Success(response[0])

    except requests.RequestException as e:
        return Error(code=-32000, message=f"Network error: {str(e)}")

@method
def list_tools(**kwargs) -> Result:
    tools = ["out_step", "in_step", "n_from_type", "e_from_type"]
    return Success({"tools": tools})

@app.route("/mcp", methods=["POST"])
def handle_mcp():
    request_data = request.get_data(as_text=True)
    try:
        response = dispatch(request_data)
        return Response(response, 200, mimetype="applications/json")
    except Exception as e:
        error_response = {
            "jsonrpc": "2.0",
            "error": {"code": -32600, "message": f"Invalid request: {str(e)}"},
            "id": None,
        }
        return Response(json.dumps(error_response), 400, mimetype="application/json")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6970, debug=True)

