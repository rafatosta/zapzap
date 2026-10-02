(() => {
  if (window._zapZapResizableChatList) {
    window._zapZapResizableChatList.setMode({resizable_enabled}, {compact_enabled});
    return;
  }
  let compactEnabled = {compact_enabled};
  let resizableEnabled = {resizable_enabled};
  const compactWidth = 80;
  const compactAttribute = 'data-zapzap-chat-list-compact';
  const compactPathAttribute = 'data-zapzap-chat-list-path';
  const chromePathAttribute = 'data-zapzap-chat-list-chrome-path';
  const compactRowAttribute = 'data-zapzap-chat-list-row';
  const avatarPathAttribute = 'data-zapzap-chat-list-avatar-path';
  const avatarAttribute = 'data-zapzap-chat-list-avatar';
  let updateMode = null;

  const resizeHandleLabel = {resize_handle_label};
  const resizeHandleHint = {resize_handle_hint};
  const savedWidthStorageKey = 'zapzap.chatListWidth';
  const minimumColumnWidth = 260;
  const minimumConversationWidth = 380;
  const keyboardResizeStep = 20;
  const columnSlotAttribute = 'data-zapzap-chat-list-slot';
  const customWidthAttribute = 'data-zapzap-chat-list-custom-width';
  const draggingAttribute = 'data-zapzap-chat-list-dragging';
  const columnWidthProperty = '--zapzap-chat-list-width';
  const resizeHandleClass = 'zapzap-chat-list-resize-handle';

  const root = document.documentElement;
  let stopResizing = null;

  const startResizing = () => {
    const stylesheet = new CSSStyleSheet();
    stylesheet.replaceSync(`
      :root[${customWidthAttribute}] [${columnSlotAttribute}] {
        flex: 0 0 var(${columnWidthProperty}) !important;
        max-width: var(${columnWidthProperty}) !important;
      }
      :root[${compactAttribute}] [${columnSlotAttribute}] {
        min-width: 0 !important;
      }
      :root[${compactAttribute}] [${columnSlotAttribute}]:not(:has(#side)) {
        flex: 0 0 min(360px, calc(100% - 380px)) !important;
        max-width: min(360px, calc(100% - 380px)) !important;
      }
      :root[${compactAttribute}] [${chromePathAttribute}] > :not([${compactPathAttribute}]) {
        display: none !important;
      }
      :root[${compactAttribute}] #side,
      :root[${compactAttribute}] [${compactPathAttribute}] {
        min-width: 0 !important;
        max-width: 100% !important;
      }
      :root[${compactAttribute}] [${compactRowAttribute}] {
        position: relative !important;
        width: 100% !important;
        overflow: hidden !important;
      }
      :root[${compactAttribute}] [${compactRowAttribute}] * {
        visibility: hidden !important;
      }
      :root[${compactAttribute}] [${avatarPathAttribute}] {
        position: static !important;
        transform: none !important;
      }
      :root[${compactAttribute}] [${avatarAttribute}] {
        position: absolute !important;
        left: 50% !important;
        top: 50% !important;
        transform: translate(-50%, -50%) !important;
        width: 49px !important;
        height: 49px !important;
        visibility: visible !important;
        cursor: pointer;
      }
      :root[${compactAttribute}] [${avatarAttribute}] * {
        visibility: visible !important;
      }
      :root[${draggingAttribute}], :root[${draggingAttribute}] * {
        cursor: col-resize !important;
        user-select: none !important;
      }
      .${resizeHandleClass} {
        position: fixed;
        width: 8px;
        margin-left: -4px;
        cursor: col-resize;
        z-index: 350;
        touch-action: none;
        outline: none;
      }
      .${resizeHandleClass}::after {
        content: "";
        position: absolute;
        top: 0;
        bottom: 0;
        left: 3px;
        width: 2px;
        background: #00a884;
        opacity: 0;
        transition: opacity .15s;
      }
      .${resizeHandleClass}:hover::after,
      .${resizeHandleClass}:focus-visible::after,
      :root[${draggingAttribute}] .${resizeHandleClass}::after {
        opacity: .7;
      }
    `);
    document.adoptedStyleSheets = [...document.adoptedStyleSheets, stylesheet];

    const resizeHandle = document.createElement('div');
    resizeHandle.className = resizeHandleClass;
    resizeHandle.title = resizeHandleHint;
    resizeHandle.tabIndex = 0;
    resizeHandle.setAttribute('role', 'separator');
    resizeHandle.setAttribute('aria-orientation', 'vertical');
    resizeHandle.setAttribute('aria-label', resizeHandleLabel);
    resizeHandle.setAttribute('aria-valuemin', String(minimumColumnWidth));
    resizeHandle.hidden = true;
    document.body.appendChild(resizeHandle);

    const readSavedWidth = () => {
      try {
        return Number.parseInt(localStorage.getItem(savedWidthStorageKey), 10) || null;
      } catch {
        return null;
      }
    };

    const persistWidth = (width) => {
      try {
        if (width) localStorage.setItem(savedWidthStorageKey, String(width));
        else localStorage.removeItem(savedWidthStorageKey);
      } catch {}
    };

    let preferredWidth = readSavedWidth();
    let chatList = null;
    let column = null;
    let isDragging = false;
    let pendingFrame = 0;

    const positionHandle = () => {
      const columnBounds = column?.isConnected ? column.getBoundingClientRect() : null;
      if (!columnBounds?.width) {
        resizeHandle.hidden = true;
        return;
      }
      resizeHandle.hidden = compactEnabled || !resizableEnabled;
      resizeHandle.setAttribute('aria-valuenow', String(Math.round(columnBounds.width)));
      resizeHandle.style.left = `${columnBounds.right}px`;
      resizeHandle.style.top = `${columnBounds.top}px`;
      resizeHandle.style.height = `${columnBounds.height}px`;
    };

    const columnResizeObserver = new ResizeObserver(positionHandle);

    const hasNativeColumnSizing = (element) => {
      const style = getComputedStyle(element);
      return style.flexGrow === '0' && style.flexBasis.endsWith('%');
    };

    const markColumnSlots = (columnContainer) => {
      column.setAttribute(columnSlotAttribute, '');
      for (const layer of columnContainer.children) {
        const overlaySlot = layer.firstElementChild;
        if (!overlaySlot || overlaySlot.hasAttribute(columnSlotAttribute)) continue;
        if (getComputedStyle(layer).position === 'absolute' && hasNativeColumnSizing(overlaySlot)) {
          overlaySlot.setAttribute(columnSlotAttribute, '');
        }
      }
    };

    const clearColumnWidth = () => {
      root.removeAttribute(customWidthAttribute);
      root.style.removeProperty(columnWidthProperty);
    };

    const widestColumnWidth = () => Math.round(
      column.parentElement.getBoundingClientRect().right
        - column.getBoundingClientRect().left
        - minimumConversationWidth,
    );

    const clearCompactMarks = () => {
      for (const attribute of [compactPathAttribute, chromePathAttribute, compactRowAttribute, avatarAttribute, avatarPathAttribute]) {
        document.querySelectorAll(`[${attribute}]`).forEach((node) => node.removeAttribute(attribute));
      }
      root.removeAttribute(compactAttribute);
    };

    const applyCompactPresentation = () => {
      clearCompactMarks();
      if (!compactEnabled || !chatList) return false;
      let avatarCount = 0;
      const rows = chatList.querySelectorAll('[role="row"], [role="listitem"], [data-testid="cell-frame-container"]');
      for (const row of rows) {
        // Prefer the outer semantic row so native selection and click routing stay intact.
        if (row.parentElement.closest('[role="row"], [role="listitem"]')) continue;
        const avatar = row.querySelector('img, [data-icon="default-user"], [data-icon="default-group"], [data-icon="default-community"]');
        if (!avatar) continue;
        for (let node = avatar.parentElement; node && node !== row; node = node.parentElement) {
          node.setAttribute(avatarPathAttribute, '');
        }
        avatar.setAttribute(avatarAttribute, '');
        row.setAttribute(compactRowAttribute, '');
        for (let node = row; node && chatList.contains(node); node = node.parentElement) {
          node.setAttribute(compactPathAttribute, '');
          if (node === chatList) break;
        }
        const listArea = row.closest('[role="grid"], [role="list"]') || row.parentElement;
        // Hide chrome outside the list, never virtual-list spacers or loading rows.
        for (let node = listArea.parentElement; node && chatList.contains(node); node = node.parentElement) {
          node.setAttribute(chromePathAttribute, '');
          if (node === chatList) break;
        }
        avatarCount++;
      }
      if (avatarCount) root.setAttribute(compactAttribute, '');
      return avatarCount > 0;
    };

    const applyColumnWidth = () => {
      if (applyCompactPresentation()) {
        root.style.setProperty(columnWidthProperty, `${compactWidth}px`);
        root.setAttribute(customWidthAttribute, '');
        return;
      }
      const widestAllowedWidth = widestColumnWidth();
      resizeHandle.setAttribute(
        'aria-valuemax',
        String(Math.max(widestAllowedWidth, minimumColumnWidth)),
      );
      if (compactEnabled || !resizableEnabled || !preferredWidth || widestAllowedWidth < minimumColumnWidth) {
        clearColumnWidth();
        return;
      }
      const columnWidth = Math.round(
        Math.min(Math.max(preferredWidth, minimumColumnWidth), widestAllowedWidth),
      );
      root.style.setProperty(columnWidthProperty, `${columnWidth}px`);
      root.setAttribute(customWidthAttribute, '');
    };

    const trackColumn = (currentColumn) => {
      if (currentColumn === column) return;
      if (column) columnResizeObserver.unobserve(column);
      column = currentColumn;
      if (column) columnResizeObserver.observe(column);
    };

    const keepAppliedWidth = () => {
      const appliedWidth = Number.parseInt(root.style.getPropertyValue(columnWidthProperty), 10);
      preferredWidth = appliedWidth || preferredWidth;
      persistWidth(preferredWidth);
    };

    const finishDrag = () => {
      if (!isDragging) return;
      isDragging = false;
      root.removeAttribute(draggingAttribute);
      keepAppliedWidth();
    };

    const syncLayout = () => {
      chatList = document.getElementById('side');
      trackColumn(chatList?.parentElement ?? null);
      const columnContainer = column?.parentElement;
      if (!columnContainer) {
        finishDrag();
        clearColumnWidth();
        clearCompactMarks();
        positionHandle();
        return;
      }
      markColumnSlots(columnContainer);
      applyColumnWidth();
      positionHandle();
    };

    const scheduleSync = () => {
      if (pendingFrame) return;
      pendingFrame = requestAnimationFrame(() => {
        pendingFrame = 0;
        syncLayout();
      });
    };

    const isInsideFrequentlyUpdatedArea = (node) =>
      chatList?.contains(node) || document.getElementById('main')?.contains(node);

    const layoutMutationObserver = new MutationObserver((mutations) => {
      if (compactEnabled || mutations.some((mutation) => !isInsideFrequentlyUpdatedArea(mutation.target))) {
        scheduleSync();
      }
    });
    layoutMutationObserver.observe(document.body, { childList: true, subtree: true });
    window.addEventListener('resize', scheduleSync);

    resizeHandle.addEventListener('pointerdown', (event) => {
      if (compactEnabled || !resizableEnabled || event.button !== 0 || !column?.isConnected) return;
      isDragging = true;
      resizeHandle.setPointerCapture(event.pointerId);
      root.setAttribute(draggingAttribute, '');
      event.preventDefault();
    });

    resizeHandle.addEventListener('pointermove', (event) => {
      if (!isDragging || !column?.isConnected) return;
      preferredWidth = Math.round(event.clientX - column.getBoundingClientRect().left);
      syncLayout();
    });

    for (const dragEndEvent of ['pointerup', 'pointercancel', 'lostpointercapture']) {
      resizeHandle.addEventListener(dragEndEvent, finishDrag);
    }

    const restoreDefaultWidth = () => {
      if (compactEnabled || !resizableEnabled) return;
      preferredWidth = null;
      persistWidth(null);
      syncLayout();
    };

    resizeHandle.addEventListener('dblclick', restoreDefaultWidth);

    resizeHandle.addEventListener('keydown', (event) => {
      if (compactEnabled || !resizableEnabled || !column?.isConnected) return;
      const currentWidth = Math.round(column.getBoundingClientRect().width);
      const widthForKey = {
        ArrowLeft: () => currentWidth - keyboardResizeStep,
        ArrowRight: () => currentWidth + keyboardResizeStep,
        Home: () => minimumColumnWidth,
        End: widestColumnWidth,
      }[event.key];
      if (widthForKey) {
        preferredWidth = widthForKey();
        syncLayout();
        keepAppliedWidth();
      } else if (event.key === 'Enter') {
        restoreDefaultWidth();
      } else {
        return;
      }
      event.preventDefault();
      event.stopPropagation();
    });

    updateMode = (resizable, compact) => {
      finishDrag();
      resizableEnabled = resizable;
      compactEnabled = compact;
      syncLayout();
    };
    syncLayout();

    stopResizing = () => {
      cancelAnimationFrame(pendingFrame);
      layoutMutationObserver.disconnect();
      columnResizeObserver.disconnect();
      window.removeEventListener('resize', scheduleSync);
      resizeHandle.remove();
      clearCompactMarks();
      document.adoptedStyleSheets = document.adoptedStyleSheets.filter(
        (adoptedStylesheet) => adoptedStylesheet !== stylesheet,
      );
      document.querySelectorAll(`[${columnSlotAttribute}]`).forEach((slot) => {
        slot.removeAttribute(columnSlotAttribute);
      });
      root.removeAttribute(customWidthAttribute);
      root.removeAttribute(draggingAttribute);
      root.style.removeProperty(columnWidthProperty);
    };
  };

  if (document.body) startResizing();
  else document.addEventListener('DOMContentLoaded', startResizing, { once: true });

  window._zapZapResizableChatList = {
    setMode(resizable, compact) {
      if (updateMode) updateMode(resizable, compact);
      else {
        resizableEnabled = resizable;
        compactEnabled = compact;
      }
    },
    destroy() {
      document.removeEventListener('DOMContentLoaded', startResizing);
      stopResizing?.();
      delete window._zapZapResizableChatList;
    },
  };
})();
