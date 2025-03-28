import asyncio
import os
from typing import List, Dict, Optional

import uuid
from playwright.async_api import async_playwright
from pydantic import BaseModel
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


class BrowserConfig(BaseModel):
    cdp_url: Optional[str] = None
    headless: bool = False


# potentially expose this to the users so they can pass in their own playwright browser that we can use, cdp or no cdp.
async def create_browser(config: BrowserConfig):
    context_manager = async_playwright()
    p_instance = await context_manager.start()
    if config.cdp_url is None:
        browser = await p_instance.chromium.launch(headless=config.headless)
    else:
        browser = await p_instance.chromium.connect_over_cdp(config.cdp_url)

    return browser, p_instance


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
            # create file or directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(self.__export_json())

    async def replay(self, cdp_url: Optional[str] = None):
        if self.task_id is None or len(self.events) == 0:
            print("No recording or events found")
            return

        browser, p_instance = await create_browser(
            BrowserConfig(
                cdp_url=cdp_url,
                headless=False,
            )
        )

        await replay_events(browser, self.events)

        await p_instance.stop()

    @staticmethod
    def from_file(path: str):
        if path.startswith("s3://"):
            s3 = boto3.client("s3")
            response = s3.get_object(Bucket="foundryml-trajectory", Key=path)
            return Recording.model_validate_json(
                response["Body"].read().decode("utf-8")
            )
        else:
            with open(path, "r") as f:
                return Recording.model_validate_json(f.read())


class Recorder:
    def __init__(self, cdp_url: str):
        self.cdp_url = cdp_url

    async def record(self):
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        print(f"Task ID: {task_id}")

        try:
            # Create browser
            browser, p_instance = await create_browser(
                BrowserConfig(
                    cdp_url=self.cdp_url,
                    headless=True,
                )
            )

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
            except Exception as e:
                print(f"Error recording: {e}")

            # close browser and context
            await context.close()
            await browser.close()
            await p_instance.stop()

            return Recording(task_id=task_id, events=events)
        except Exception as e:
            print(f"Error recording: {e}")
        finally:
            await p_instance.stop()
