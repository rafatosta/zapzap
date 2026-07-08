(function () {
  if (window.__zapzapCtrlArrowVisualNavigationFixInstalled) {
    return;
  }

  window.__zapzapCtrlArrowVisualNavigationFixInstalled = true;

  document.addEventListener(
    "keydown",
    function (event) {
      if (
        !event.ctrlKey ||
        event.altKey ||
        event.metaKey ||
        (event.key !== "ArrowLeft" && event.key !== "ArrowRight")
      ) {
        return;
      }

      const selection = window.getSelection();

      if (!selection || selection.rangeCount === 0) {
        return;
      }

      const anchorNode = selection.anchorNode;

      const element =
        anchorNode && anchorNode.nodeType === Node.ELEMENT_NODE
          ? anchorNode
          : anchorNode && anchorNode.parentElement;

      if (!element || !element.closest('[contenteditable="true"]')) {
        return;
      }

      if (typeof selection.modify !== "function") {
        return;
      }

      event.preventDefault();
      event.stopImmediatePropagation();

      /*
       * Use visual word navigation instead of logical navigation.
       *
       * This fixes Ctrl+Arrow movement in RTL text while preserving the
       * expected behavior in LTR text inside WhatsApp Web editable fields.
       */
      const direction = event.key === "ArrowLeft" ? "left" : "right";
      const action = event.shiftKey ? "extend" : "move";

      selection.modify(action, direction, "word");
    },
    true
  );
})();
