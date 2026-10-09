/* Route PDF card clicks through WhatsApp's own download controls.
 * Qt's PdfViewerEnabled setting cannot change WhatsApp's in-page viewer.
 * Do not fetch/decrypt media, force cross-origin URLs, or inspect message data.
 */
(() => {
    "use strict";

    const initialMode = __ZAPZAP_PDF_CLICK_MODE__;
    const existing = window.__zapzapPdfClicks;
    if (existing) {
        existing.setMode(initialMode);
        return;
    }

    const PDF = /\.pdf(?:\b|$)/i;
    const DOWNLOAD = /(?:download|indir|herunterladen|descargar|télécharger|baixar|scarica)/i;
    const CLOSE = /(?:close|kapat|fechar|cerrar|schließen)/i;
    let mode = initialMode;
    let observer = null;
    let expiry = null;
    let pending = false;
    let checked = false;

    const isDownloadButton = (node) => {
        if (!node || !node.getAttribute) return false;
        if (node.matches("a[download]")) return true;
        const fields = [
            node.getAttribute("aria-label") || "",
            node.getAttribute("title") || "",
            node.getAttribute("data-testid") || "",
            node.getAttribute("data-icon") || "",
        ].join(" ");
        return DOWNLOAD.test(fields) ||
            !!node.querySelector('[data-icon*="download"], [data-testid*="download"]');
    };

    const isCloseButton = (node) => {
        const fields = [
            node.getAttribute("aria-label") || "",
            node.getAttribute("title") || "",
            node.getAttribute("data-testid") || "",
        ].join(" ");
        return CLOSE.test(fields) ||
            !!node.querySelector('[data-icon="x"], [data-icon="close"]');
    };

    const buttons = (root) => Array.from(
        root.querySelectorAll("button, [role='button'], a[download]")
    );

    const findPdfCard = (target) => {
        if (!target || !target.closest) return null;
        const message = target.closest("[data-id], [data-testid='msg-container']");
        const documentCard = target.closest('[data-testid*="document"], [data-testid*="file"]');
        const root = documentCard || message;
        if (!root) return null;

        // Never change unrelated media, chat messages or PDF text references.
        const marksDocument = !!documentCard ||
            !!root.querySelector('[data-testid*="document"], [data-icon*="document"]');
        if (!marksDocument) return null;
        const label = ((documentCard && documentCard.innerText) ||
                       (message && message.innerText) || "").slice(0, 500);
        return PDF.test(label) ? (documentCard || message) : null;
    };

    function stopWatching() {
        if (observer) observer.disconnect();
        if (expiry) clearTimeout(expiry);
        observer = null;
        expiry = null;
        pending = false;
        checked = false;
    }

    const viewerContainers = () => document.querySelectorAll(
        '[role="dialog"], [data-testid*="media-viewer"], ' +
        '[data-testid*="document-viewer"], [data-animate-modal-popup]'
    );

    const downloadFromViewer = () => {
        if (!pending || checked || mode !== "download") return;
        for (const viewer of viewerContainers()) {
            const button = buttons(viewer).find(isDownloadButton);
            if (!button) continue;
            checked = true;
            button.click();
            // A delayed close lets WhatsApp initiate its download request.
            setTimeout(() => {
                if (mode === "download" && viewer.isConnected) {
                    const close = buttons(viewer).find(isCloseButton);
                    if (close) close.click();
                }
                stopWatching();
            }, 350);
            return;
        }
    };

    function watchViewer() {
        stopWatching();
        pending = true;
        const root = document.documentElement;
        if (!root) return;
        observer = new MutationObserver(downloadFromViewer);
        observer.observe(root, {childList: true, subtree: true});
        expiry = setTimeout(stopWatching, 5000);
        downloadFromViewer();
    }

    function onClick(event) {
        if (mode !== "download" || !event.isTrusted) return;
        if (!(event.target instanceof Element)) return;
        if (event.target.closest("button, [role='button'], a[download]") &&
            isDownloadButton(event.target.closest("button, [role='button'], a[download]"))) {
            return;
        }
        const card = findPdfCard(event.target);
        if (!card) return;
        const root = event.target.closest("[data-id], [data-testid='msg-container']") || card;
        const direct = buttons(root).find(isDownloadButton);
        if (direct && !direct.contains(event.target)) {
            event.preventDefault();
            event.stopImmediatePropagation();
            direct.click();
            return;
        }
        // WhatsApp has no visible card download button in some versions.
        // Let it open the preview and use its own download action as fallback.
        watchViewer();
    }

    document.addEventListener("click", onClick, true);
    window.__zapzapPdfClicks = {
        setMode(next) {
            mode = next === "download" ? "download" : "preview";
            if (mode !== "download") stopWatching();
        },
        getMode() { return mode; },
    };
})();
