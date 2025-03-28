from typing import Optional
from enum import Enum

from playwright.async_api import Page
from pydantic import BaseModel, ConfigDict

# Event type constants
# Refer to https://github.com/rrweb-io/rrweb/blob/master/docs/recipes/dive-into-event.md for more details
EVENT_TYPES = {
    "LOADED": 0,
    "INITAL_LOAD": 1,
    "FULL_SNAPSHOT": 2,
    "INCREMENTAL_SNAPSHOT": 3,
    "META": 4,
    "CUSTOM": 5,
}

# In these kinds of events, the incrementalSnapshotEvent is the event that contains incremental data. You can use `event.data.source` to find which kind of incremental data it belongs to:
# Refer to https://github.com/rrweb-io/rrweb/blob/master/docs/recipes/dive-into-event.md for more details
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
    "PAGE_LOAD": 9,
}

interactable_sources = [
    EVENT_SOURCES["INPUT"],
    EVENT_SOURCES["MOUSE_INTERACTION"],
    EVENT_SOURCES["MEDIA_INTERACTION"],
]


class EventSnapshot(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    timestamp: int
    dom_content: str
    event_type: int
    is_user_triggered: bool

    metadata: Optional[dict] = None
    element: Optional[str] = None
    event_source: Optional[int] = None


async def generate_event_snapshots(
    page: Page, event: dict, start_timestamp: int
) -> Optional[EventSnapshot]:
    """
    Generates a snapshot of the DOM state at a specific event timestamp during web recording replay.

    This function:
    1. Adds the event to the rrweb player
    2. Navigates to the specific timestamp
    3. Captures the DOM state from the replayer iframe
    4. For interactive events (clicks, inputs, etc.), captures the specific element that was interacted with

    Args:
        page (Page): Playwright page object containing the rrweb replayer
        event (dict): rrweb event object containing:
            - type: Event type (e.g., FULL_SNAPSHOT, INCREMENTAL_SNAPSHOT)
            - timestamp: When the event occurred
            - data: Event-specific data including:
                - source: Type of interaction (e.g., MOUSE_INTERACTION, INPUT)
                - id: Node ID for interactive events
                - userTriggered: Whether event was triggered by user
        start_timestamp (int): Base timestamp to calculate offset from

    Returns:
        EventSnapshot: EventSnapshot containing:
            - timestamp: When the event occurred
            - dom_content: HTML snapshot of the page state
            - event_type: Type of rrweb event
            - element: HTML of the interacted element (if applicable)
            - is_user_triggered: Whether event was user-initiated
            - event_source: Type of interaction
        None: If snapshot cannot be generated (e.g., invalid iframe state)

    Example:
        ```python
        # Example event object
        event = {
            "type": 3,  # INCREMENTAL_SNAPSHOT
            "timestamp": 1234567890,
            "data": {
                "source": 2,  # MOUSE_INTERACTION
                "id": 42,
                "userTriggered": True
            }
        }

        # Generate snapshot
        snapshot = await generate_event_snapshots(page, event, start_timestamp=1234567000)

        # Access snapshot data
        print(snapshot["dom_content"])  # HTML of the page
        print(snapshot["element"])      # HTML of clicked element
        ```
    """
    is_user_triggered = event["data"].get("userTriggered", False)
    event_type = event["type"]
    event_source = event["data"].get("source")
    timestamp = event["timestamp"]
    element = None
    # Go to specific timestamp
    offset = timestamp - start_timestamp
    await page.evaluate("offset => window.player.goto(offset, false)", offset)

    # Get the iframe element
    iframe = await page.query_selector(".replayer-wrapper > iframe")
    if not iframe:
        return None

    # Get the frame content
    frame = await iframe.content_frame()
    if not frame:
        return None

    snapshot = await frame.content()

    if (
        snapshot is None
        or snapshot.strip() == ""
        or snapshot.startswith('<html class="rrweb-paused"><head></head>')
    ):
        return None

    # Get the element that was interacted with
    if event_source in interactable_sources:
        node_id = event["data"].get("id", None)
        if node_id is not None:
            with open("web_recorder/js/get_rrweb_dom_node.js", "r") as f:
                js_code = f.read()
            element = await page.evaluate(js_code, [node_id, event_source])

    return EventSnapshot(
        timestamp=timestamp,
        dom_content=snapshot,
        event_type=event_type,
        element=element,
        is_user_triggered=is_user_triggered,
        event_source=event_source,
    )


async def generate_dom_events(page: Page, events: list) -> list[EventSnapshot]:
    """Collect DOM snapshots for each event"""
    dom_snapshots = []

    start_timestamp = events[0]["timestamp"]

    seen_events = set()
    for i, event in enumerate(events):
        event_key = f"{event['timestamp']}-{event['type']}"
        if event_key in seen_events or event["type"] in [
            EVENT_TYPES["LOADED"],
            EVENT_TYPES["INITAL_LOAD"],
        ]:
            continue

        seen_events.add(event_key)

        snapshot = await generate_event_snapshots(page, event, start_timestamp)

        if snapshot is None:
            continue

        if event["type"] == EVENT_TYPES["META"]:
            dom_snapshots.append(
                EventSnapshot(
                    timestamp=event["timestamp"],
                    dom_content="",
                    event_type=event["type"],
                    is_user_triggered=True,
                    event_source=EVENT_SOURCES["NAVIGATION"],
                    metadata=event["data"],
                )
            )

        # This is a custom event that is emitted when the page is loaded from the setup_recording.js script
        # We use this to get the initial page load snapshot once network is loaded.
        # This works for client side rendered apps unlike standard load events from rrweb,
        elif (
            event["type"] == EVENT_TYPES["CUSTOM"]
            and event["data"]["payload"]
            and event["data"]["tag"] == "page-load"
        ):
            payload = event["data"]["payload"]

            dom_snapshots.append(
                EventSnapshot(
                    timestamp=event["timestamp"],
                    dom_content=payload["state"],
                    event_type=event["type"],
                    is_user_triggered=True,
                    event_source=EVENT_SOURCES["PAGE_LOAD"],
                    metadata={
                        "url": payload["url"],
                    },
                )
            )
        else:
            dom_snapshots.append(snapshot)

    return dom_snapshots


class TrajectoryAction(Enum):
    CLICK = "click"
    HOVER = "hover"
    MOUSE_MOVE = "mouse_move"
    SCROLL = "scroll"
    VIEWPORT_RESIZE = "viewport_resize"
    INPUT = "input"
    NAVIGATION = "navigation"
    PAGE_LOAD = "page_load"


class TrajectorySnapshot(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    action: TrajectoryAction
    timestamp: int
    state: str

    element: Optional[str] = None
    metadata: Optional[dict] = None


def create_trajectory_snapshot(snapshot: EventSnapshot) -> Optional[TrajectorySnapshot]:
    """Create a trajectory from an event snapshot"""
    event_source = snapshot.event_source
    element = snapshot.element

    if event_source is None:
        return None

    if event_source == EVENT_SOURCES["MOUSE_INTERACTION"]:
        action = (
            TrajectoryAction.HOVER
            if element and ":hover" in element
            else TrajectoryAction.CLICK
        )
    elif event_source == EVENT_SOURCES["MOUSE_MOVE"]:
        action = TrajectoryAction.MOUSE_MOVE
    elif event_source == EVENT_SOURCES["SCROLL"]:
        action = TrajectoryAction.SCROLL
    elif event_source == EVENT_SOURCES["VIEWPORT_RESIZE"]:
        action = TrajectoryAction.VIEWPORT_RESIZE
    elif event_source == EVENT_SOURCES["INPUT"]:
        action = TrajectoryAction.INPUT
    elif event_source == EVENT_SOURCES["NAVIGATION"]:
        action = TrajectoryAction.NAVIGATION
    elif event_source == EVENT_SOURCES["PAGE_LOAD"]:
        action = TrajectoryAction.PAGE_LOAD
    else:
        return None

    return TrajectorySnapshot(
        action=action,
        element=element,
        timestamp=snapshot.timestamp,
        state=snapshot.dom_content,
        metadata=snapshot.metadata,
    )
