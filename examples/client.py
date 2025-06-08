import json
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
)

# MCP server endpoint
MCP_SERVER_URL = "http://localhost:6969"

def get_previous_month_timestamp():
    """Calculate the Unix timestamp for the start of the previous month."""
    now = datetime.now()
    previous_month = now - relativedelta(months=1)
    previous_month_start = previous_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return int(previous_month_start.timestamp())

def send_mcp_request(tool_name: str, args: dict, connection_id: str = None) -> dict:
    """Send a request to the MCP server and return the parsed response."""
    payload = {
        "tool": {
            "tool_name": tool_name,
            "args": args
        }
    }
    if connection_id:
        payload["connection_id"] = str(connection_id)

    try:
        response = requests.post(f"{MCP_SERVER_URL}/call_tool", json=payload, timeout=10)
        logger.info(f"Request to {tool_name}: {payload}")
        logger.info(f"Response from {tool_name}: {response.text}")

        if response.status_code != 200:
            logger.error(f"Failed to call {tool_name}: HTTP {response.status_code}")
            return {"status_code": response.status_code, "result": None}

        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error calling {tool_name}: {e}")
        return {"status_code": 500, "result": None}
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse {tool_name} response: {e}")
        return {"status_code": 500, "result": None}

def traverse_patients_visits(name: str, date: int) -> list:
    """Traverse the graph via MCP server to get visits for a patient by name, with visits on or after the given date."""
    # Step 1: Initialize connection
    init_response = send_mcp_request("init", {"connection_addr": "localhost", "connection_port": 6969})
    if init_response.get("status_code") != 200 or not init_response.get("result"):
        logger.error("Failed to initialize connection")
        return []
    connection_id = init_response["result"]
    logger.info(f"Initialized connection: {connection_id}")

    # Step 2: Get Patient nodes
    patient_response = send_mcp_request("n_from_type", {"node_type": "Patient"}, connection_id)
    if patient_response.get("status_code") != 200:
        logger.error("Failed to get Patient nodes")
        return []
    patients = patient_response.get("result", [])
    logger.info(f"Patient nodes: {patients}")

    # Step 3: Filter patients by name
    filter_args = {"properties": [["name", name]]}
    filter_response = send_mcp_request("filter_items", filter_args, connection_id)
    if filter_response.get("status_code") != 200:
        logger.error("Failed to filter patients by name")
        return []
    filtered_patients = filter_response.get("result", [])
    logger.info(f"Filtered patients: {filtered_patients}")

    # Step 4: Get outgoing Visit edges
    visit_response = send_mcp_request("out_e_step", {"edge_label": "Visit"}, connection_id)
    if visit_response.get("status_code") != 200:
        logger.error("Failed to get Visit edges")
        return []
    visits = visit_response.get("result", [])
    logger.info(f"Visit edges: {visits}")

    # Step 5: Filter visits by date (date >= provided date)
    date_filter_args = {"properties": [["date", str(date)]]}
    final_response = send_mcp_request("filter_items", date_filter_args, connection_id)
    if final_response.get("status_code") != 200:
        logger.error("Failed to filter visits by date")
        return []
    filtered_visits = final_response.get("result", [])
    logger.info(f"Filtered visits: {filtered_visits}")

    return filtered_visits

if __name__ == "__main__":
    # Example usage
    patient_name = "Milo Dean"  # Replace with a valid patient name in your database
    date_timestamp = get_previous_month_timestamp()  # Start of previous month
    logger.info(f"Querying visits for patient '{patient_name}' on or after {date_timestamp}")

    visits = traverse_patients_visits(patient_name, date_timestamp)
    logger.info(f"Final visits: {visits}")

