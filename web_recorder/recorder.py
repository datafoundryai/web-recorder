import asyncio
import uuid
import json
from playwright.async_api import async_playwright, Page, ConsoleMessage, Browser
import os
from pydantic import BaseModel
from typing import List, Dict
import boto3

from scrapybara import Scrapybara
from web_recording.replayer import replay_events
from web_recording.utils import get_js_path

no_automation_args = [
    "--no-sandbox",
    "--disable-blink-features=AutomationControlled",
    "--disable-infobars",
    "--disable-background-timer-throttling",
    "--disable-popup-blocking",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
    "--disable-window-activation",
    "--disable-focus-on-load",
    "--no-first-run",
    "--no-default-browser-check",
    "--no-startup-window",
    "--window-position=0,0",
    "--disable-site-isolation-trials",
    "--disable-features=IsolateOrigins,site-per-process",
]





def parse_logs(log: ConsoleMessage):
    print("recording browser logs", log)

    log = log.text

    # if log.startswith("<session_event>"):
    #     events_str = log.strip("<session_event>")
    #     events_data = json.loads(events_str)

    #     print("events_data", events_data)

    #     store_events(events_data)


class Recording(BaseModel):
    task_id: str
    events: List[Dict]

    def __init__(self, task_id: str, events: List[Dict]):
        self.task_id = task_id
        self.events = events
        self.browser = browser

    def __export_json(self):
        return self.model_dump_json()

    def __export_s3(self):
        s3 = boto3.client("s3")
        s3.put_object(
            Key=f"recording_{self.task_id}.json",
            Body=self.__export_json(),
        )

    def export(self, path: str):
        if path.startswith("s3://"):
            self.__export_s3()
        else:
            with open(path, "w") as f:
                f.write(self.__export_json())

    def replay(self, browser: Browser):
        # TODO: replay the recording
        # using the browser create a new page
        context = browser.contexts[0]
        page = context.new_page()

        replay_events(page, self.events)

class Recorder():
    def __init__(self, cdp_url: str):
        self.cdp_url = cdp_url

    async def record(self):
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        print(f"Task ID: {task_id}")

        async with async_playwright() as p:
            # Launch browser
            # browser = await p.chromium.launch(headless=False, args=no_automation_args)

            # Connect to the remote session
            browser = await p.chromium.connect_over_cdp(self.cdp_url)
            # browser = await p.chromium.connect_over_cdp("ws://127.0.0.1:59939/devtools/browser/dbe9bb61-bda3-4b92-910c-c1763beba1df")

            # Create context
            context = await browser.new_context(
                # viewport={"width": 1280, "height": 720},
                bypass_csp=True,
            )

            context.on("console", parse_logs)
            # context.on("message", store_events)
            # context.on("session", store_events)

            events = []

            def store_events(data):
                nonlocal events
                if data["events"]:
                    events.extend(data["events"])

            await context.expose_function("store_events", store_events)

            # Inject rrweb and recording scripts
            await context.add_init_script(path=get_js_path("rrweb.js"))
            # custom code that injects task id and sets up recording
            await context.add_init_script(script=f"window.taskId = '{task_id}';")
            await context.add_init_script(
                path=get_js_path("setup_recording.js"),
            )
            # Create new page
            page = await context.new_page()
            completed_trajectory = False

            async def handle_close(page):
                # handle close
                # await context.close()
                # await browser.close()
                nonlocal completed_trajectory
                completed_trajectory = True

            page.on("close", handle_close)

            try:
                # Keep browser open for interaction
                # print("Browser is ready for interaction. Press Ctrl+C to exit.")
                while not completed_trajectory:
                    await asyncio.sleep(1)
            finally:
                await context.close()
                await browser.close()

            return Recording(task_id=task_id, events=events)


if __name__ == "__main__":
    recording = asyncio.run(record())
    print("recording", recording.model_dump_json())
