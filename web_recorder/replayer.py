import asyncio
import time

from playwright.async_api import Page, Browser, BrowserContext

from web_recorder.utils import (
    generate_dom_events,
    create_trajectory_snapshot,
)


async def setup_player(page: Page, events: list):
    # check if player is already setup
    is_player_available = await page.evaluate("typeof player !== 'undefined'")
    if is_player_available:
        return False

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
                    useVirtualDom: true,
                }
            });
            window.player = player;
        }
    """,
        [events],
    )

    return True


async def inject_rrweb_player_js(context: BrowserContext):
    await context.add_init_script(path="web_recorder/rrweb/rrweb.js")
    await context.add_init_script(path="web_recorder/rrweb/rrweb-player.js")


async def inject_rrweb_player_css(page: Page):
    await page.add_style_tag(
        path="web_recorder/rrweb/rrweb-stylesheet.css"
    )


async def replay_events(browser: Browser, events: list):
    # fix event timestamps
    try:
        context = await browser.new_context(
            bypass_csp=True,
        )

        await inject_rrweb_player_js(context)

        page = await context.new_page()
        await inject_rrweb_player_css(page)

        # Initial setup
        await wait_for_player(page)

        # player requires at least 2 events to start
        # Can't send all events because if we have a lot of events during init, the player freezes.
        rrweb_required_events = 2
        await setup_player(page, events[:rrweb_required_events])

        # Add remaining events
        for event in events[rrweb_required_events:]:
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

    await inject_rrweb_player_js(context)

    page = await context.new_page()

    try:
        await wait_for_player(page)

        if not await setup_player(page, events):
            raise Exception("Player not available")

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
