import asyncio
import uuid
from playwright.async_api import async_playwright, Browser
from pydantic import BaseModel
from typing import List, Dict
import boto3

from web_recorder.replayer import replay_events
from web_recorder.utils import get_js_path

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


class Recording(BaseModel):
    task_id: str
    events: List[Dict]

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


class Recorder:
    def __init__(self, cdp_url: str):
        self.cdp_url = cdp_url

    async def record(self):
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        print(f"Task ID: {task_id}")

        async with async_playwright() as p:
            # Launch browser

            # Connect to the remote session
            browser = await p.chromium.connect_over_cdp(self.cdp_url)

            # Create context
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                bypass_csp=True,
            )

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
                nonlocal completed_trajectory
                completed_trajectory = True

            page.on("close", handle_close)

            try:
                # Keep browser open for interaction
                while not completed_trajectory:
                    await asyncio.sleep(1)
            finally:
                await context.close()
                await browser.close()

            return Recording(task_id=task_id, events=events)
