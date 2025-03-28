([nodeId, eventSource]) => {
  const node = window.player.getMirror().getNode(nodeId);

  // Events referenced from here: https://github.com/rrweb-io/rrweb/blob/fd9d2747c6a236975055a69165ccce640b029015/docs/recipes/dive-into-event.md
  const CLICKABLE_EVENT_SOURCES = [2];
  if (!node) return null;

  if (CLICKABLE_EVENT_SOURCES.includes(eventSource)) {
    // Traverse up to find clickable elements instead of the subnode that was clicked directly
    let current = node;
    const interactable_tags = [
      "A",
      "BUTTON",
      "INPUT",
      "TEXTAREA",
      "SELECT",
      "OPTION",
      "LABEL",
      "CHECKBOX",
      "RADIO",
    ];
    while (
      current &&
      current.textContent.trim() === node.textContent.trim() &&
      current.tagName !== "BODY"
    ) {
      if (
        interactable_tags.includes(current.tagName) ||
        current.getAttribute("role") === "button"
      ) {
        return current.outerHTML;
      }
      current = current.parentElement;
    }

    if (
      !current ||
      !interactable_tags.includes(current.tagName) ||
      current.getAttribute("role") !== "button"
    ) {
      return node.outerHTML;
    }

    return current.outerHTML;
  }

  return node.outerHTML;
};
