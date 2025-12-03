(function () {
    "use strict";

    const STORAGE_KEY_WAS_ENABLED_FOR_HOST = "__darkreader__wasEnabledForHost";
    function wasEnabledForHost() {
        try {
            const value = sessionStorage.getItem(
                STORAGE_KEY_WAS_ENABLED_FOR_HOST
            );
            if (value === "true") {
                return true;
            }
            if (value === "false") {
                return false;
            }
        } catch (err) {}
        return null;
    }

    if (
        document.documentElement instanceof HTMLHtmlElement &&
        matchMedia("(prefers-color-scheme: dark)").matches &&
        wasEnabledForHost() !== false &&
        !document.querySelector(".darkreader--fallback") &&
        !document.querySelector(".darkreader")
    ) {
        const css = [
            "html, body, body :not(iframe) {",
            "    background-color: #181a1b !important;",
            "    border-color: #776e62 !important;",
            "    color: #e8e6e3 !important;",
            "}",
            "html, body {",
            "    opacity: 1 !important;",
            "    transition: none !important;",
            "}",
            'div[style*="background-color: rgb(135, 135, 135)"] {',
            "    background-color: #878787 !important;",
            "}"
        ].join("\n");
        const fallback = document.createElement("style");
        fallback.classList.add("darkreader");
        fallback.classList.add("darkreader--fallback");
        fallback.media = "screen";
        fallback.textContent = css;
        if (document.head) {
            document.head.append(fallback);
        } else {
            const root = document.documentElement;
            root.append(fallback);
            const observer = new MutationObserver(() => {
                if (document.head) {
                    observer.disconnect();
                    if (fallback.isConnected) {
                        document.head.append(fallback);
                    }
                }
            });
            observer.observe(root, {childList: true});
        }
    }
})();
