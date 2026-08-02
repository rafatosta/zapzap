(function () {
  if (window.__zapzapSendWithCtrlEnterInstalled) {
    return;
  }

  window.__zapzapSendWithCtrlEnterInstalled = true;

  // WhatsApp Web already knows both gestures: Enter sends, Shift+Enter starts a
  // new line. Its message box is a Lexical editor, which tells the two apart by
  // the Shift modifier alone. Rather than sending or editing anything
  // ourselves, we relabel the modifiers of the key event before WhatsApp reads
  // it, so its own handlers do the work: Enter is read as Shift+Enter, and
  // Ctrl+Enter as Enter.
  //
  // The event stays the original trusted one, so a handler that refuses
  // synthetic events is not a problem. If WhatsApp ever stops reading the
  // relabelled modifier, its handler treats the key as a send and this option
  // silently stops working; nothing is inserted twice and no keystroke is
  // swallowed.

  // A modifier is exposed twice, as a property and through getModifierState,
  // and the two have to agree: shadowing only the property would leave the
  // event contradicting itself for any handler that reads the method.
  function relabel(event, property, modifier, value) {
    try {
      Object.defineProperty(event, property, {
        value: value,
        configurable: true,
      });
      const inherited = event.getModifierState.bind(event);
      Object.defineProperty(event, 'getModifierState', {
        value: function (key) {
          return key === modifier ? value : inherited(key);
        },
        configurable: true,
      });
    } catch (e) {
      // Leave the event as it is; WhatsApp keeps its own behaviour.
    }
  }

  function messageBox(target) {
    if (!target || typeof target.closest !== 'function') return null;

    const editable = target.closest('[contenteditable="true"]');
    if (!editable || editable.getAttribute('role') !== 'textbox') return null;

    // The chat list and the new chat drawer live in the side panel, and their
    // search fields must keep sending on Enter.
    if (editable.closest('#side')) return null;

    // The message box, the caption of an outgoing file and the edit box sit in
    // the composer footer; the search fields do not. Anything we cannot place
    // is left alone, so a layout this does not recognize turns the option off
    // rather than breaking a field. Re-check both landmarks against the page
    // whenever WhatsApp Web changes its markup.
    if (!editable.closest('footer')) return null;

    return editable;
  }

  function suggesting(editable) {
    // Enter picks the highlighted entry while a mention, emoji or command list
    // is open, and that is not a send. These two attributes are the standard
    // way a text box says a list is open; WhatsApp Web is expected, but not
    // confirmed, to use them.
    return editable.hasAttribute('aria-activedescendant') ||
      editable.getAttribute('aria-expanded') === 'true';
  }

  window.addEventListener('keydown', function (e) {
    // Shift+Enter already starts a new line, and Alt+Enter is not ours.
    if (e.key !== 'Enter' || e.shiftKey || e.altKey) return;
    // Let an input method finish composing before Enter means anything.
    if (e.isComposing || e.keyCode === 229) return;

    const editable = messageBox(e.target);
    if (!editable || suggesting(editable)) return;

    if (e.ctrlKey || e.metaKey) {
      // Command is the send chord on macOS, Control everywhere else.
      relabel(e, 'ctrlKey', 'Control', false);
      relabel(e, 'metaKey', 'Meta', false);
    } else {
      relabel(e, 'shiftKey', 'Shift', true);
    }
  }, true); // capture on window, the first stop before WhatsApp's own handlers
})();
