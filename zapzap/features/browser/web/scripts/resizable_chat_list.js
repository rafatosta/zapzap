(() => {
  if (window._zapZapResizableChatList) return;

  const resizeHandleLabel = {resize_handle_label};
  const resizeHandleHint = {resize_handle_hint};
  const savedWidthStorageKey = 'zapzap.chatListWidth';
  const minimumColumnWidth = 85;
  const compactThreshold = 200;
  const compactAttribute = 'data-zapzap-chat-list-compact';
  const minimumConversationWidth = 380;
  const keyboardResizeStep = 20;
  const handleReachDistance = 8;
  const columnSlotAttribute = 'data-zapzap-chat-list-slot';
  const customWidthAttribute = 'data-zapzap-chat-list-custom-width';
  const draggingAttribute = 'data-zapzap-chat-list-dragging';
  const columnWidthProperty = '--zapzap-chat-list-width';
  const resizeHandleClass = 'zapzap-chat-list-resize-handle';

  const root = document.documentElement;
  let stopResizing = null;
  let applyMinimumWidth = null;
  let compactRequested = false;

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
      :root[${compactAttribute}] #side header,
      :root[${compactAttribute}] #side [data-zapzap-chat-list-controls] {
        display: none !important;
      }
      :root[${compactAttribute}] [data-zapzap-chat-list-static-row] { position: relative; }
      :root[${compactAttribute}] [data-zapzap-chat-list-unread-path] {
        position: static !important;
        overflow: visible !important;
      }
      :root[${compactAttribute}] [data-zapzap-chat-list-unread] {
        position: absolute !important;
        top: 6px;
        left: 40px;
        z-index: 1;
        pointer-events: none;
      }
      [data-zapzap-new-chat-source] { display: none !important; }
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
    let previousWidth = null;
    const decoratedRows = new Map();
    let chatList = null;
    let column = null;
    let isDragging = false;
    let pendingFrame = 0;
    let columnRightEdge = null;

    let newChatSource = null;
    let newChatProxy = null;

    const restoreNewChat = () => {
      newChatSource?.removeAttribute('data-zapzap-new-chat-source');
      newChatProxy?.remove();
      newChatSource = null;
      newChatProxy = null;
    };

    const syncNewChat = () => {
      const compact = root.hasAttribute(compactAttribute);
      if (!compact || !column?.isConnected) {
        restoreNewChat();
        return;
      }
      // Keep React's source in its original tree and forward the action to it.
      const source = [...column.querySelectorAll('button')].find((button) =>
        button.querySelector('svg title')?.textContent === 'wds-ic-new-chat-filled');
      const actions = document.querySelectorAll('button, [role="tab"], [role="button"]');
      let rail = null;
      for (const action of actions) {
        if (column.contains(action) || action === newChatProxy) continue;
        for (let node = action.parentElement; node && node !== document.body; node = node.parentElement) {
          const bounds = node.getBoundingClientRect();
          if (bounds.left <= 24 && bounds.width >= 48 && bounds.width <= 120 &&
              bounds.height >= window.innerHeight * 0.5 &&
              getComputedStyle(node).visibility !== 'hidden') {
            rail = node;
            break;
          }
        }
        if (rail) break;
      }
      if (!source || !rail) {
        restoreNewChat();
        return;
      }
      const firstAction = [...rail.querySelectorAll('button, [role="tab"], [role="button"]')]
        .find((action) => action !== newChatProxy);
      if (!firstAction) { restoreNewChat(); return; }
      let item = firstAction;
      while (item.parentElement !== rail && item.parentElement) {
        const parent = item.parentElement;
        const style = getComputedStyle(parent);
        if (style.display === 'flex' && style.flexDirection === 'column') break;
        item = parent;
      }
      if (source !== newChatSource || !newChatProxy?.isConnected) {
        restoreNewChat();
        newChatSource = source;
        newChatProxy = source.cloneNode(true);
        newChatProxy.removeAttribute('id');
        newChatProxy.querySelectorAll('[id]').forEach((node) => node.removeAttribute('id'));
        newChatProxy.removeAttribute('data-zapzap-new-chat-source');
        newChatProxy.setAttribute('data-zapzap-component', 'compact-new-chat');
        newChatProxy.style.cssText = 'display:flex;align-items:center;justify-content:center;align-self:center;flex-shrink:0;width:40px;height:40px;margin:4px;padding:8px;';
        newChatProxy.addEventListener('click', () => {
          if (newChatSource?.isConnected && !newChatSource.disabled &&
              newChatSource.getAttribute('aria-disabled') !== 'true') newChatSource.click();
        });
        newChatSource.setAttribute('data-zapzap-new-chat-source', '');
      }
      newChatProxy.disabled = source.disabled;
      for (const attribute of ['aria-label', 'aria-disabled', 'title']) {
        const value = source.getAttribute(attribute);
        if (value === null) newChatProxy.removeAttribute(attribute);
        else newChatProxy.setAttribute(attribute, value);
      }
      if (newChatProxy.parentElement !== item.parentElement || newChatProxy.nextElementSibling !== item) {
        item.parentElement.insertBefore(newChatProxy, item);
      }
    };

    const restoreRows = () => {
      for (const [row, title] of decoratedRows) {
        if (title === null) row.removeAttribute('title');
        else row.setAttribute('title', title);
        row.removeAttribute('data-zapzap-chat-list-row');
        row.removeAttribute('data-zapzap-chat-list-static-row');
      }
      decoratedRows.clear();
      chatList?.querySelectorAll('[data-zapzap-chat-list-unread], [data-zapzap-chat-list-unread-path], [data-zapzap-chat-list-controls]')
        .forEach((node) => {
          node.removeAttribute('data-zapzap-chat-list-unread');
          node.removeAttribute('data-zapzap-chat-list-unread-path');
          node.removeAttribute('data-zapzap-chat-list-controls');
        });
    };

    const syncCompactRows = () => {
      if (!root.hasAttribute(compactAttribute)) { restoreRows(); return; }
      if (!chatList) return;
      for (const [row, title] of decoratedRows) {
        if (chatList.contains(row)) continue;
        if (title === null) row.removeAttribute('title');
        else row.title = title;
        row.removeAttribute('data-zapzap-chat-list-row');
        row.removeAttribute('data-zapzap-chat-list-static-row');
        decoratedRows.delete(row);
      }
      // Mark native controls, leaving React ownership and event handlers intact.
      for (const control of chatList.querySelectorAll(
        'input, [role="search"], [role="searchbox"], [role="tablist"], [data-testid="chat-list-filters"]',
      )) {
        let wrapper = control;
        while (wrapper.parentElement !== chatList && wrapper.parentElement &&
               !wrapper.parentElement.querySelector('[role="grid"], [role="row"], [role="listitem"]')) {
          wrapper = wrapper.parentElement;
        }
        wrapper.setAttribute('data-zapzap-chat-list-controls', '');
      }
      for (const row of chatList.querySelectorAll('[role="row"], [role="listitem"]')) {
        const name = row.querySelector('span[title], [data-testid="cell-frame-title"]')?.getAttribute('title') ||
          row.querySelector('[data-testid="cell-frame-title"]')?.textContent ||
          row.querySelector('img[alt]')?.alt;
        if (!name) continue;
        if (!decoratedRows.has(row)) {
          decoratedRows.set(row, row.getAttribute('title'));
          // Virtualized rows must keep their absolute position and transforms.
          if (getComputedStyle(row).position === 'static') {
            row.setAttribute('data-zapzap-chat-list-static-row', '');
          }
        }
        if (row.title !== name) row.title = name;
        row.setAttribute('data-zapzap-chat-list-row', '');
        row.querySelectorAll('[data-zapzap-chat-list-unread], [data-zapzap-chat-list-unread-path]').forEach(
          (node) => {
            node.removeAttribute('data-zapzap-chat-list-unread');
            node.removeAttribute('data-zapzap-chat-list-unread-path');
          });
        // Native unread counters expose a numeric value and an accessible label.
        const unread = row.querySelector('[data-testid="icon-unread-count"]') ||
          [...row.querySelectorAll('span[aria-label]')].find((node) => /^\d+$/.test(node.textContent.trim()));
        unread?.setAttribute('data-zapzap-chat-list-unread', '');
        for (let node = unread?.parentElement; node && node !== row; node = node.parentElement) {
          node.setAttribute('data-zapzap-chat-list-unread-path', '');
        }
      }
    };

    const positionHandle = () => {
      const columnBounds = column?.isConnected ? column.getBoundingClientRect() : null;
      if (!columnBounds?.width) {
        resizeHandle.hidden = true;
        columnRightEdge = null;
        return;
      }
      resizeHandle.hidden = false;
      columnRightEdge = columnBounds.right;
      resizeHandle.setAttribute('aria-valuenow', String(Math.round(columnBounds.width)));
      resizeHandle.style.left = `${columnBounds.right}px`;
      resizeHandle.style.top = `${columnBounds.top}px`;
      resizeHandle.style.height = `${columnBounds.height}px`;
      root.toggleAttribute(compactAttribute, columnBounds.width < compactThreshold);
      syncCompactRows();
      syncNewChat();
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
      root.removeAttribute(compactAttribute);
      restoreRows();
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
        restoreNewChat();
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
      if (root.hasAttribute(compactAttribute) && mutations.some((mutation) => chatList?.contains(mutation.target))) {
        syncCompactRows();
      }
      if (mutations.some((mutation) => !isInsideFrequentlyUpdatedArea(mutation.target) ||
          mutation.target.closest?.('header'))) {
        scheduleSync();
      }
    });
    layoutMutationObserver.observe(document.body, { childList: true, characterData: true, subtree: true, attributes: true,
      attributeFilter: ['title', 'aria-label'] });
    window.addEventListener('resize', scheduleSync);

    const isColumnEdgeExposedAt = (clientY) => {
      const elementAtColumnEdge = document
        .elementsFromPoint(columnRightEdge - 1, clientY)
        .find((element) => element !== resizeHandle);
      return Boolean(elementAtColumnEdge?.closest(`[${columnSlotAttribute}]`));
    };

    const updateHandleReachability = (event) => {
      if (isDragging || columnRightEdge === null) return;
      if (Math.abs(event.clientX - columnRightEdge) > handleReachDistance) return;
      const isReachable = isColumnEdgeExposedAt(event.clientY);
      resizeHandle.style.pointerEvents = isReachable ? '' : 'none';
    };

    document.addEventListener('pointermove', updateHandleReachability, { capture: true, passive: true });

    resizeHandle.addEventListener('pointerdown', (event) => {
      if (event.button !== 0 || !column?.isConnected) return;
      if (!isColumnEdgeExposedAt(event.clientY)) {
        resizeHandle.style.pointerEvents = 'none';
        return;
      }
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

    applyMinimumWidth = () => {
      finishDrag();
      if ((preferredWidth ?? column?.getBoundingClientRect().width) < compactThreshold) {
        preferredWidth = previousWidth;
      } else {
        previousWidth = preferredWidth;
        preferredWidth = minimumColumnWidth;
      }
      persistWidth(preferredWidth);
      syncLayout();
    };
    if (compactRequested) applyMinimumWidth();
    else syncLayout();

    stopResizing = () => {
      cancelAnimationFrame(pendingFrame);
      layoutMutationObserver.disconnect();
      columnResizeObserver.disconnect();
      window.removeEventListener('resize', scheduleSync);
      document.removeEventListener('pointermove', updateHandleReachability, { capture: true });
      restoreNewChat();
      restoreRows();
      root.removeAttribute(compactAttribute);
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
    compact() {
      compactRequested = true;
      applyMinimumWidth?.();
    },
    destroy() {
      document.removeEventListener('DOMContentLoaded', startResizing);
      stopResizing?.();
      delete window._zapZapResizableChatList;
    },
  };
})();
