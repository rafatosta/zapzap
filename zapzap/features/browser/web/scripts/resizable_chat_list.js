(() => {
  if (window._zapZapResizableChatList) return;

  const resizeHandleLabel = {resize_handle_label};
  const resizeHandleHint = {resize_handle_hint};
  const savedWidthStorageKey = 'zapzap.chatListWidth';
  const minimumColumnWidth = 80;
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
        min-width: 0 !important;
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
      resizeHandle.hidden = false;
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

    const applyColumnWidth = () => {
      const widestAllowedWidth = widestColumnWidth();
      resizeHandle.setAttribute(
        'aria-valuemax',
        String(Math.max(widestAllowedWidth, minimumColumnWidth)),
      );
      if (!preferredWidth || widestAllowedWidth < minimumColumnWidth) {
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
      if (mutations.some((mutation) => !isInsideFrequentlyUpdatedArea(mutation.target))) {
        scheduleSync();
      }
    });
    layoutMutationObserver.observe(document.body, { childList: true, subtree: true });
    window.addEventListener('resize', scheduleSync);

    resizeHandle.addEventListener('pointerdown', (event) => {
      if (event.button !== 0 || !column?.isConnected) return;
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
      preferredWidth = null;
      persistWidth(null);
      syncLayout();
    };

    resizeHandle.addEventListener('dblclick', restoreDefaultWidth);

    resizeHandle.addEventListener('keydown', (event) => {
      if (!column?.isConnected) return;
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

    syncLayout();

    stopResizing = () => {
      cancelAnimationFrame(pendingFrame);
      layoutMutationObserver.disconnect();
      columnResizeObserver.disconnect();
      window.removeEventListener('resize', scheduleSync);
      resizeHandle.remove();
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
    destroy() {
      document.removeEventListener('DOMContentLoaded', startResizing);
      stopResizing?.();
      delete window._zapZapResizableChatList;
    },
  };
})();
