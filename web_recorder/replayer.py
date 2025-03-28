import asyncio
import time

from playwright.async_api import Page, Browser

from web_recorder.utils import generate_dom_events, create_trajectory_snapshot


async def setup_player(page: Page, events: list):
    # check if player is already setup
    is_player_available = await page.evaluate("typeof player !== 'undefined'")
    if is_player_available:
        return False

    # player requires at least 2 events to start
    # Can't send all events because if we have a lot of events during init, the player freezes.
    required_events = 2

    await page.evaluate(
        """
        ([events]) => {
            console.log({ events })
            const player = new rrwebPlayer({
                target: document.body,
                props: {
                    events: events,
                    showController: true,
                    autoPlay: false,
                    showWarning: true,
                    mouseTail: false,
                    useVirtualDom: true
                }
            });
            window.player = player;
        }
    """,
        [events[:required_events]],
    )

    return True


async def replay_events(browser: Browser, events: list):
    # fix event timestamps
    events = fix_event_timestamps(events)

    try:
        context = await browser.new_context(
            bypass_csp=True,
        )
        page = await context.new_page()

        # Setup rrweb injection on navigation
        async def handle_navigation():
            try:
                player_available = await page.evaluate("typeof player !== 'undefined'")
                if player_available:
                    return

                # Inject rrweb player
                await inject_rrweb_player(page)
                # Setup player
                await setup_player(page, events)

                print("rrweb player setup after navigation")
            except Exception as e:
                print(f"Error setting up rrweb player after navigation: {e}")

        def handle_navigation_wrapper():
            tasks = [
                t for t in asyncio.all_tasks() if t.get_name() == "inject_rrweb_player"
            ]
            if not tasks:
                task = asyncio.create_task(
                    handle_navigation(), name="inject_rrweb_player"
                )
                task.add_done_callback(
                    lambda t: t.exception()
                    and print(f"Error in rrweb injection: {t.exception()}")
                )

        # Listen for frame navigation events
        page.on("framenavigated", handle_navigation_wrapper)
        page.on("load", handle_navigation_wrapper)
        page.on("domcontentloaded", handle_navigation_wrapper)

        # Initial setup
        await inject_rrweb_player(page)
        await setup_player(page, events[:2])

        # Add remaining events
        for event in events[2:]:
            await page.evaluate("([event]) => window.player.addEvent(event)", [event])

        await page.evaluate("() => window.player.play()")

        completed_replay = False

        async def handle_close(page):
            nonlocal completed_replay
            completed_replay = True

        page.on("close", handle_close)

        try:
            while not completed_replay:
                await asyncio.sleep(1)
        finally:
            await context.close()
            await browser.close()
    except Exception as e:
        print(f"Error replaying events: {e}")


def fix_event_timestamps(events: list):
    """Fix event timestamps to not have duplicates"""
    for i in range(1, len(events)):
        if events[i]["timestamp"] == events[i - 1]["timestamp"]:
            events[i]["timestamp"] = events[i - 1]["timestamp"] + 1
    return events


async def wait_for_player(page: Page, timeout: int = 30):
    """
    Wait for the rrweb player to be available.
    This is a helper function to wait for the player to be available before
    setting up the player.

    Args:
        page: The page to wait for the player on.
        timeout: The timeout for the player to be available in seconds.

    Raises:
        Exception: If the player is not available after the timeout.

    Returns:
        None
    """
    start_time = time.time()
    while True:
        rrweb_player_available = await page.evaluate(
            "typeof rrwebPlayer !== 'undefined'"
        )
        if rrweb_player_available:
            break

        await asyncio.sleep(1)

        if time.time() - start_time > timeout:
            raise Exception("Player not available after timeout")


async def build_trajectory_snapshots(browser: Browser, events: list):
    """Build the DOM for the events and generate trajectory snapshots"""

    # Create context and page
    context = await browser.new_context(
        bypass_csp=True,
    )
    await context.add_init_script(path="web_recorder/rrweb/rrweb.js")
    await context.add_init_script(path="web_recorder/rrweb/rrweb-player.js")

    page = await context.new_page()

    try:
        await wait_for_player(page)

        if not await setup_player(page, events):
            raise Exception("Player not available")

        # Fix timestamps
        events = fix_event_timestamps(events)
        dom_events = await generate_dom_events(page, events)

        trajectory_snapshots = [
            create_trajectory_snapshot(event) for event in dom_events
        ]
        return [snapshot for snapshot in trajectory_snapshots if snapshot is not None]

    except Exception as e:
        print(f"Error building DOM: {e}")
        raise e
    finally:
        await context.close()
