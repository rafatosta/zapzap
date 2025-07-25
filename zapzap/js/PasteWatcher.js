(function () {
  function isInsideWhatsapp(target) {
    return (
      location.hostname.includes('web.whatsapp.com') &&
      target instanceof HTMLElement &&
      target.closest('[contenteditable="true"], div.copyable-text')
    );
  }

  function isLikelyURL(text) {
    try {
      const url = new URL(text.trim());
      return url.protocol === "http:" || url.protocol === "https:";
    } catch {
      return false;
    }
  }

  function handlePasteInWhatsapp(event) {
    if (!isInsideWhatsapp(event.target)) return;

    const clipboard = event.clipboardData;
    const items = clipboard.items;
    const results = [];
    const promises = [];

    console.error('[PasteWatcher] Types:', clipboard.types);

    // Try to directly get the URI list if available
    if (clipboard.types.includes('text/uri-list')) {
      const uriList = clipboard.getData('text/uri-list');
      if (uriList) {
        results.push(`🔗 URI list detected:\n${uriList.trim()}`);
      } else {
        results.push('⚠️ Type "text/uri-list" detected, but no content returned via getData.');
      }
    }

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      console.error(`[PasteWatcher] item[${i}]: kind=${item.kind}, type=${item.type}`);

      if (item.kind === 'file') {
        const file = item.getAsFile();
        results.push(`🖼️ File: ${file.name || '[unnamed]'}\nType: ${file.type}\nSize: ${file.size} bytes`);
      } else if (item.kind === 'string' && item.type !== 'text/uri-list') {
        const promise = new Promise((resolve) => {
          item.getAsString((str) => {
            if (isLikelyURL(str)) {
              resolve(`🔗 Link detected:\n${str.trim()}`);
            } else {
              resolve(`📄 Pasted text:\n${str.trim()}`);
            }
          });
        });
        promises.push(promise);
      }
    }

    Promise.all(promises).then((strings) => {
      const final = results.concat(strings);
      if (final.length > 0) {
        alert('[WAWeb] Clipboard content:\n\n' + final.join('\n\n'));
      } else {
        alert('[WAWeb] Nothing detected in the clipboard.');
      }
    });
  }

  document.addEventListener('paste', handlePasteInWhatsapp, true);
  console.error('[PasteWatcher] Active with content detection on WhatsApp Web');
})();
