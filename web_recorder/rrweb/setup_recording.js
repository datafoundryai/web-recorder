// Initialize events array
if (window.stopFn) {
  console.log("rrweb recording already started");
  return;
}

if (!window.taskId) {
  console.log("taskId not found");
  return;
}

const unsupportedUrlStrings = [
  "about:blank",
  "about:srcdoc",
  "googletagmanager",
  "td.doubleclick.net",
  "googleadservices",
];

// check if window is iframe
if (window.self !== window.top) {
  console.log("window is iframe, won't record");
  return;
}

if (unsupportedUrlStrings.some((str) => window.location.href.includes(str))) {
  console.log(`unsupported url: ${window.location.href} found, won't record`);
  return;
}

console.log("Starting rrweb recording");

if (!window.events) {
  window.events = [];
}

// Start recording
window.stopFn = rrweb.record({
  emit(event) {
    window.events.push(event);
  },
  userTriggeredOnInput: true,
  inlineImages: false,
  inlineStylesheet: true,
  maskInputOptions: {
    password: false,
  },
});

// Add custom event for page load completion
window.addEventListener("load", () => {
  rrweb.record.addCustomEvent("page-load", {
    url: window.location.href,
    timestamp: Date.now(),
    state: document.documentElement.outerHTML,
  });
});

// Function to send events via beacon
window.sendEventsBG = () => {
  console.log("send events bg called");
  if (window.events && window.events.length > 0) {
    const eventsToSend = [...window.events];

    console.log("Sending session events", eventsToSend);
    // Using sendBeacon to send events
    navigator.sendBeacon(
      "http://localhost:8002/api/events",
      JSON.stringify({
        task_id: window.taskId,
        events: eventsToSend,
      })
    );

    // Clear sent events
    window.events = [];
  }
};

window.sendEvents = async () => {
  console.log("send events called");
  if (window.events && window.events.length > 0) {
    const eventsToSend = [...window.events];
    window.events = [];

    try {
      await window.store_events({
        task_id: window.taskId,
        events: eventsToSend,
      });
    } catch (error) {
      console.error("Lost events:", error);
    }
  }
};

// Set up periodic sending (every 1 seconds)
window.sendEventsInterval = setInterval(window.sendEvents, 1000);

// Still keep unload handler as a backup
window.addEventListener("beforeunload", (event) => {
  event.preventDefault();

  if (window.stopFn) {
    window.stopFn();
  }

  // Clear the interval
  if (window.sendEventsInterval) {
    clearInterval(window.sendEventsInterval);
  }

  // Send any remaining events
  window.sendEvents();
});

// Also send events when tab becomes hidden
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "hidden") {
    window.sendEvents();
  }
});
