import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright, Page

# Event type constants
EVENT_TYPES = {"FULL_SNAPSHOT": 2, "PAGE_INFO": 4, "INCREMENTAL_SNAPSHOT": 3}

# In these kinds of events, the incrementalSnapshotEvent is the event that contains incremental data. You can use `event.data.source` to find which kind of incremental data it belongs to:

EVENT_SOURCES = {
    "MUTATION": 0,
    "MOUSE_MOVE": 1,
    "MOUSE_INTERACTION": 2,
    "SCROLL": 3,
    "VIEWPORT_RESIZE": 4,
    "INPUT": 5,
    "TOUCH_MOVE": 6,
    "MEDIA_INTERACTION": 7,
    "NAVIGATION": 8,
}


async def inject_rrweb_player(page: Page):
    if page.is_closed():
        return

    # check if rrweb-player is already injected
    is_player_available = await page.evaluate("typeof rrwebPlayer !== 'undefined'")
    if is_player_available:
        return

    await page.add_style_tag(
        url="https://cdn.jsdelivr.net/npm/rrweb-player@2.0.0-alpha.18/dist/style.css"
    )
    await page.add_script_tag(path="foundryml/trajectory/rrweb/rrweb-player.js")

    try:
        await page.wait_for_load_state("networkidle")
    except Exception as e:
        print(f"Warning: Unable to wait for network idle: {e}")

    # Verify rrweb-player is available
    max_retries = 3
    retries = 0
    while retries < max_retries:
        is_player_available = await page.evaluate("typeof rrwebPlayer !== 'undefined'")
        if is_player_available:
            break
        retries += 1
        await asyncio.sleep(1)
    if not is_player_available:
        raise Exception("rrweb-player failed to load properly")


def get_trajectories(events_directory: str):
    """Read trajectories from events directory"""
    if not os.path.exists(events_directory):
        raise Exception(f"Events directory {events_directory} does not exist")

    trajectories = []
    for file in os.listdir(events_directory):
        if file.endswith(".json"):
            file_path = Path(events_directory) / file
            with open(file_path, "r") as f:
                events = json.load(f)
            trajectory_id = file.split(".")[0].split("_")[1]
            trajectories.append(
                {
                    "id": trajectory_id,
                    "events": events if isinstance(events, list) else events.flat(),
                }
            )
    return trajectories


async def setup_player(page: Page, events: list, page_info: dict):
    # check if player is already setup
    is_player_available = await page.evaluate("typeof player !== 'undefined'")
    if is_player_available:
        return

    """Setup rrweb-player with events using page dimensions from page_info"""
    width = page_info["data"]["width"]
    height = page_info["data"]["height"]

    width = max(width, 1280)
    height = max(height, 720)

    print("number of events", len(events))

    # player requires at least 2 events to start, if we have a lot of events, the player freezes.
    required_events = 2

    await page.evaluate(
        """
        ([events, width, height]) => {
            console.log({ events })
            const player = new rrwebPlayer({
                target: document.body,
                props: {
                    events: events,
                    width: width,
                    height: height,
                    showController: true,
                    autoPlay: true,
                    showWarning: true,
                    mouseTail: false,
                    useVirtualDom: true
                }
            });
            window.player = player;
        }
    """,
        [events[:required_events], width, height],
    )

async def replay_events(page: Page, events: list):
    for event in events:
        await page.evaluate("([event]) => window.player.addEvent(event)", [event])

    await page.evaluate("() => window.player.play()")


async def collect_dom_snapshots(page: Page, events: list):
    """Collect DOM snapshots for each event"""
    dom_snapshots = []

    start_timestamp = events[0]["timestamp"]

    page_info = None
    for event in events:
        is_user_triggered = event["data"].get("userTriggered", False)
        event_type = event["type"]
        event_source = event["data"].get("source")
        timestamp = event["timestamp"]

        # Go to specific timestamp
        offset = timestamp - start_timestamp
        await page.evaluate("([event]) => window.player.addEvent(event)", [event])
        await page.evaluate("offset => window.player.goto(offset, false)", offset)

        # Get the iframe element
        iframe = await page.query_selector(".replayer-wrapper > iframe")
        if not iframe:
            continue

        # Get the frame content
        frame = await iframe.content_frame()
        if not frame:
            continue

        if event_type == EVENT_TYPES["PAGE_INFO"]:
            page_info = event
            continue

        snapshot = await frame.content()

        if (
            snapshot is None
            or snapshot.strip() == ""
            or snapshot.startswith('<html class="rrweb-paused"><head></head>')
        ):
            continue

        if page_info is not None:
            dom_snapshots.append(
                {
                    "timestamp": event["timestamp"],
                    "dom_content": snapshot,
                    "event_type": event_type,
                    "is_user_triggered": True,
                    "event_source": EVENT_SOURCES["NAVIGATION"],
                }
            )
            page_info = None

        dom_snapshots.append(
            {
                "timestamp": timestamp,
                "dom_content": snapshot,
                "event_type": event_type,
                "is_user_triggered": is_user_triggered,
                "event_source": event_source,
            }
        )

    return dom_snapshots


async def generate_state_action_pairs(dom_snapshots: list):
    """Generate state action pairs from DOM snapshots"""
    state_action_pairs = []

    for snapshot in [
        ds
        for ds in dom_snapshots
        if ds["event_source"] is not None and ds["is_user_triggered"]
    ]:
        event_source = snapshot["event_source"]

        if event_source is None:
            continue

        dom = snapshot["dom_content"]

        if event_source == EVENT_SOURCES["MOUSE_INTERACTION"]:
            action = "click"
        elif event_source == EVENT_SOURCES["MOUSE_MOVE"]:
            action = "mouse_move"
        elif event_source == EVENT_SOURCES["SCROLL"]:
            action = "scroll"
        elif event_source == EVENT_SOURCES["VIEWPORT_RESIZE"]:
            action = "viewport_resize"
        elif event_source == EVENT_SOURCES["INPUT"]:
            action = "input"
        elif event_source == EVENT_SOURCES["NAVIGATION"]:
            action = "navigation"
        else:
            continue

        state_action_pairs.append({"state": dom, "action": action})

    return state_action_pairs


def fix_event_timestamps(events: list):
    """Fix event timestamps to not have duplicates"""
    for i in range(1, len(events)):
        if events[i]["timestamp"] == events[i - 1]["timestamp"]:
            events[i]["timestamp"] = events[i - 1]["timestamp"] + 1
    return events


events_directory = "foundryml/trajectory/events"  # Replace with your directory
pairs_directory = "foundryml/trajectory/pairs"  # Replace with your directory


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


async def main():
    # Get trajectories
    trajectories = get_trajectories(events_directory)
    print(f"Found {len(trajectories)} trajectories")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=no_automation_args)
        # Create pairs directory if it doesn't exist
        pairs_dir = Path(pairs_directory)
        pairs_dir.mkdir(exist_ok=True)

        for trajectory in trajectories:
            print(f"\nProcessing trajectory {trajectory['id']}")

            # Check if pairs file already exists
            pairs_file = pairs_dir / f"trajectory_pairs_{trajectory['id']}.json"
            if pairs_file.exists():
                print(f"Pairs file already exists for trajectory {trajectory['id']}, skipping...")
                continue

            # Get page info events
            page_info = next(
                (
                    e
                    for e in trajectory["events"]
                    if e["type"] == EVENT_TYPES["PAGE_INFO"]
                ),
                None,
            )

            if not page_info:
                page_info = {
                    "data": {
                        "width": 1280,
                        "height": 720,
                    },
                    "timestamp": 0,
                    "type": EVENT_TYPES["PAGE_INFO"],
                }

            page_info["data"]["width"] = max(page_info["data"]["width"], 1280)
            page_info["data"]["height"] = max(page_info["data"]["height"], 720)

            # for _event_page in event_pages:
            context = await browser.new_context(
                viewport={
                    "width": page_info["data"]["width"],
                    "height": page_info["data"]["height"],
                }
            )
            page = await context.new_page()

            # Setup rrweb injection on navigation
            async def handle_navigation():
                try:
                    player_available = await page.evaluate(
                        "typeof player !== 'undefined'"
                    )
                    if player_available:
                        return

                    # Inject rrweb player
                    await inject_rrweb_player(page)

                    # Setup player
                    await setup_player(page, trajectory["events"], page_info)

                    print("rrweb player setup after navigation")
                except Exception as e:
                    print(f"Error setting up rrweb player after navigation: {e}")

            def handle_navigation_wrapper():
                tasks = [
                    t
                    for t in asyncio.all_tasks()
                    if t.get_name() == "inject_rrweb_player"
                ]
                if not tasks:
                    task = asyncio.create_task(
                        handle_navigation(), name="inject_rrweb_player"
                    )
                    # Add error handling callback to prevent unhandled exceptions
                    task.add_done_callback(
                        lambda t: t.exception()
                        and print(f"Error in rrweb injection: {t.exception()}")
                    )

            # Listen for frame navigation events
            page.on("framenavigated", handle_navigation_wrapper)
            page.on("load", handle_navigation_wrapper)
            page.on("domcontentloaded", handle_navigation_wrapper)

            # Inject rrweb player
            await inject_rrweb_player(page)

            # Setup player
            await setup_player(page, trajectory["events"], page_info)

            # Collect DOM snapshots
            # wait for any async tasks to complete
            while tasks := asyncio.tasks.all_tasks():
                if any(task.get_name() == "inject_rrweb_player" for task in tasks):
                    print(f"Waiting for script to be injected...")
                    await asyncio.sleep(3)
                else:
                    break

            try:
                print("Fixing event timestamps")
                trajectory["events"] = fix_event_timestamps(trajectory["events"])

                print("Collecting DOM snapshots")
                dom_snapshots = await collect_dom_snapshots(page, trajectory["events"])

                # Generate state action pairs from snapshots
                state_action_pairs = await generate_state_action_pairs(dom_snapshots)

                # Write state action pairs to file
                with open(pairs_file, "w") as f:
                    json.dump(state_action_pairs, f, indent=2)

                print(
                    f"Wrote {len(state_action_pairs)} state-action pairs to {pairs_file}"
                )
            except Exception as e:
                print(f"Error collecting DOM snapshots: {e}")
            await page.close()

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
