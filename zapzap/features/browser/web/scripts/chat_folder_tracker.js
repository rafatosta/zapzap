(() => {
  // Tell ZapZap which chat is open so downloads can go into a folder named
  // after it. The last pointer press decides: inside the conversation pane or
  // the right drawer (contact or group info and its media, which belong to the
  // open chat) it reports the chat title, inside the rest of the main screen
  // (chat list, left drawers, the all-chats media gallery) it reports no chat, and on floating layers (media viewer, menus)
  // it keeps the previous value unless the header now shows another chat
  // (switched with the keyboard), in which case it reports no chat.
  window._zapZapChatFolderTracker?.destroy();

  const chatTitleSelector =
    'header [data-testid="conversation-info-header-chat-title"]';
  const mainScreenSelector = '[data-testid="wa-web-main-screen"]';
  const chatDrawerSelector = '[data-testid="drawer-right"]';
  // The all-chats media gallery is a floating dialog that the right drawer can
  // open too; its files may come from any chat.
  const mediaGallerySelector = '[data-testid="media-hub-modal"]';

  let current = '';
  let lastSent = null;

  const titleText = (element) => {
    if (!element) return '';
    const title = element.getAttribute('title');
    if (title && title.trim()) return title.trim();
    let text = '';
    const walk = (node) => {
      for (const child of node.childNodes) {
        if (child.nodeType === Node.TEXT_NODE) text += child.nodeValue;
        // WhatsApp draws emoji as images; their alt text keeps the emoji.
        else if (child.nodeName === 'IMG') text += child.getAttribute('alt') || '';
        else walk(child);
      }
    };
    walk(element);
    return text.trim();
  };

  const openChatTitle = () => {
    const main = document.getElementById('main');
    return main ? titleText(main.querySelector(chatTitleSelector)) : '';
  };

  // Returns the chat title to report, '' for no chat, or null to keep it.
  const classify = (target) => {
    const main = target.closest('#main');
    if (main) return titleText(main.querySelector(chatTitleSelector));
    if (target.closest(chatDrawerSelector)) return openChatTitle();
    if (target.closest(mediaGallerySelector)) return '';
    const screen = document.querySelector(mainScreenSelector);
    if (screen) return screen.contains(target) ? '' : null;
    return target.closest('#side, [data-testid^="drawer"]') ? '' : null;
  };

  // Uses the single QWebChannel opened by the theme controller. Without a
  // bridge lastSent stays put, so a later press retries the same value.
  const publish = () => {
    const bridge = window._zapZapWAWebThemeController?.bridge;
    if (!bridge || typeof bridge.on_active_chat_changed !== 'function') return;
    if (lastSent === current) return;
    bridge.on_active_chat_changed(current);
    lastSent = current;
  };

  const onPointerDown = (event) => {
    const target = event.target;
    if (!target || typeof target.closest !== 'function') return;
    const value = classify(target);
    if (value !== null) current = value;
    // A floating layer keeps the chat only while the header still shows it.
    else if (current !== '' && openChatTitle() !== current) current = '';
    publish();
  };

  const listenerOptions = { capture: true, passive: true };
  document.addEventListener('pointerdown', onPointerDown, listenerOptions);

  window._zapZapChatFolderTracker = {
    current() {
      return current;
    },
    reset() {
      current = '';
      lastSent = null;
    },
    destroy() {
      document.removeEventListener('pointerdown', onPointerDown, listenerOptions);
      delete window._zapZapChatFolderTracker;
    },
  };
})();
