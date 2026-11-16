"""Paste clipboard images into WhatsApp Web without rewriting the clipboard.

QtWebEngine reads clipboard images through ``QMimeData.imageData()`` and a
QImage round trip. For browser "Copy image" selections (Chromium, Brave,
Vivaldi) that path can hand the page no file at all, so Ctrl+V does nothing
(#284, #974). Instead of normalizing the global clipboard, ZapZap reads the
raw image bytes itself and gives them to the page as a ``File`` through a
synthetic paste event, the same mechanism the plain-text paste already uses
for WhatsApp's composer.
"""

import base64
import json
from dataclasses import dataclass

from PyQt6.QtCore import QBuffer, QIODevice


# Preferred order: PNG is lossless and what browsers and screenshot tools
# publish; the others are passed through untouched when they are all there is.
IMAGE_MIME_TYPES = ("image/png", "image/jpeg", "image/webp", "image/gif")

# A selection that offers any of these is text first (spreadsheets, rich text
# with an image preview, terminals). It keeps the native paste. The X11 names
# appear for XWayland sources.
TEXT_FORMATS = ("text/plain", "UTF8_STRING", "STRING", "TEXT")

# Base64 travels through runJavaScript; keep a ceiling well above WhatsApp's
# own media limits so a pathological clipboard cannot stall the UI thread.
MAX_IMAGE_BYTES = 64 * 1024 * 1024

_EXTENSIONS = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/webp": "webp",
    "image/gif": "gif",
}


@dataclass(frozen=True)
class ClipboardImage:
    data: bytes
    mime_type: str

    @property
    def filename(self) -> str:
        return "image." + _EXTENSIONS.get(self.mime_type, "png")


def _has_real_text(formats) -> bool:
    # QMimeData.hasText() is also true when the selection only carries URLs,
    # which is exactly what a browser's "Copy image" publishes next to the
    # PNG. Look for an actual text representation instead.
    return any(
        fmt in TEXT_FORMATS or fmt.startswith("text/plain;") for fmt in formats
    )


def _has_local_files(mime) -> bool:
    # Files copied in a file manager already reach the page as Files through
    # the native paste.
    try:
        return mime.hasUrls() and any(url.isLocalFile() for url in mime.urls())
    except RuntimeError:
        return False


def clipboard_image(clipboard):
    """Return the clipboard image as a ClipboardImage, or None.

    None means "leave Ctrl+V to QtWebEngine": no image, real text present,
    copied files, or an image too large to inject. The clipboard is only read.
    """
    if clipboard is None:
        return None
    mime = clipboard.mimeData()
    if mime is None:
        return None
    formats = list(mime.formats())
    if _has_real_text(formats) or _has_local_files(mime):
        return None

    for mime_type in IMAGE_MIME_TYPES:
        if mime_type in formats:
            data = bytes(mime.data(mime_type))
            if data:
                return _within_limit(ClipboardImage(data, mime_type))

    # In-process selections (e.g. "Copy image" inside ZapZap) may only carry
    # application/x-qt-image.
    if mime.hasImage():
        image = clipboard.image()
        if not image.isNull():
            buffer = QBuffer()
            try:
                buffer.open(QIODevice.OpenModeFlag.WriteOnly)
                if image.save(buffer, "PNG"):
                    return _within_limit(
                        ClipboardImage(bytes(buffer.data()), "image/png")
                    )
            finally:
                buffer.close()
    return None


def _within_limit(image):
    return image if len(image.data) <= MAX_IMAGE_BYTES else None


_IMAGE_PASTE_SCRIPT = r"""
(function () {
    const payload = __PAYLOAD__;
    let bytes;
    if (typeof Uint8Array.fromBase64 === "function") {
        bytes = Uint8Array.fromBase64(payload.data);
    } else {
        const binary = atob(payload.data);
        bytes = new Uint8Array(binary.length);
        for (let index = 0; index < binary.length; index++) {
            bytes[index] = binary.charCodeAt(index);
        }
    }
    const file = new File([bytes], payload.name, {
        type: payload.type, lastModified: Date.now(),
    });
    const transfer = () => {
        const data = new DataTransfer();
        data.items.add(file);
        return data;
    };

    const editableAncestor = (node) => {
        let element = node && (
            node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement
        );
        while (element) {
            if (element.isContentEditable) return element;
            element = element.parentElement;
        }
        return null;
    };
    const selection = window.getSelection();
    const active = document.activeElement;
    const target = (
        (active && active !== document.body ? active : null)
        || editableAncestor(selection && selection.anchorNode)
        || document.body
    );

    // WhatsApp's handler cancels the paste when it takes the file; a
    // synthetic paste has no default action of its own.
    const pasteEvent = new ClipboardEvent("paste", {
        clipboardData: transfer(), bubbles: true, cancelable: true,
        composed: true,
    });
    target.dispatchEvent(pasteEvent);
    if (pasteEvent.defaultPrevented) return "paste";

    // Fallback: drop the file on the open conversation, which WhatsApp also
    // turns into the attachment preview.
    const zone = document.querySelector("#main");
    if (!zone) return "none";
    const dropData = transfer();
    let dropped = false;
    for (const type of ["dragenter", "dragover", "drop"]) {
        const dragEvent = new DragEvent(type, {
            dataTransfer: dropData, bubbles: true, cancelable: true,
            composed: true,
        });
        zone.dispatchEvent(dragEvent);
        if (type === "drop") dropped = dragEvent.defaultPrevented;
    }
    return dropped ? "drop" : "none";
})();
"""


def image_paste_script(image: ClipboardImage) -> str:
    """Build the script that hands ``image`` to the focused page as a File."""
    payload = json.dumps({
        "data": base64.b64encode(image.data).decode("ascii"),
        "type": image.mime_type,
        "name": image.filename,
    })
    return _IMAGE_PASTE_SCRIPT.replace("__PAYLOAD__", payload)
