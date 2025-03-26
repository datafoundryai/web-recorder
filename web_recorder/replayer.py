import asyncio
from playwright.async_api import Page, Browser


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
    await page.add_script_tag(path="web_recorder/rrweb/rrweb-player.js")

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


async def setup_player(page: Page, events: list):
    # check if player is already setup
    is_player_available = await page.evaluate("typeof player !== 'undefined'")
    if is_player_available:
        return

    print("number of events", len(events))

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
