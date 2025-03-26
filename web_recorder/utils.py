from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from datetime import datetime
import uuid
from importlib import resources

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.post("/api/events")
def store_events(data: dict):

    print('store_events called with data', data)

    task_id = data.get("task_id")
    events = data.get("events", [])

    if not task_id:
        return {"error": "task_id is required"}
    
    os.makedirs("foundryml/trajectory/events", exist_ok=True)

    # Use a single file for the task
    filename = os.path.join("foundryml/trajectory/events", f"trajectory_{task_id}.json")

    # Load existing events if file exists
    existing_events = []
    if os.path.exists(filename):
        with open(filename, "r") as f:
            existing_events = json.load(f)

    # Append new events
    existing_events.extend(events)

    # # Sort all events by timestamp
    # existing_events.sort(key=lambda x: x["timestamp"])

    # Write all events back to file
    with open(filename, "w") as f:
        json.dump(existing_events, f)

    return {"status": "success", "filename": filename}



def get_js_path(js_filename):
    """Get path to a JS file in the package."""
    try:
        # For Python 3.9+
        with resources.files("web_recorder.rrweb").joinpath(js_filename) as path:
            return str(path)
    except Exception:
        # For older Python versions
        with resources.path("web_recorder.rrweb", js_filename) as path:
            return str(path)