(function () {
  if (window.__zapzapCtrlArrowVisualNavigationFixInstalled) {
    return;
  }

  window.__zapzapCtrlArrowVisualNavigationFixInstalled = true;

  document.addEventListener('keydown', function (e) {
    if (!e.ctrlKey || (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight')) return;
    const sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) return;
    const el = sel.anchorNode && sel.anchorNode.parentElement;
    if (!el || !el.closest('[contenteditable="true"]')) return;

    e.preventDefault();
    e.stopImmediatePropagation();

    const direction = e.key === 'ArrowLeft' ? 'left' : 'right'; // visual, not logical
    const alter = e.shiftKey ? 'extend' : 'move';
    sel.modify(alter, direction, 'word');
  }, true); // capture phase, so it runs before WhatsApp's own handlers
})();
