// Silences WhatsApp Web's message tone while the desktop is in Do Not Disturb.
// Python prefixes the source with the initial value of
// window.__zapzapNotificationSoundInitial (so a reload never starts unmuted)
// and toggles window.__zapzapNotificationSound.setSuppressed(true|false) live.
//
// The tone is an <audio> element that is never attached to the DOM, served
// from static.whatsapp.net and not looping. Voice notes (blob: sources),
// videos (attached <video>) and the looping call ringtone do not match.
// Fail open: anything unrecognised plays normally.

(function () {
    if (window.__zapzapNotificationSound) return;

    const state = {
        suppressed: window.__zapzapNotificationSoundInitial === true,
        setSuppressed(value) {
            this.suppressed = !!value;
        },
    };
    Object.defineProperty(window, "__zapzapNotificationSound", { value: state });

    const isMessageTone = (media) =>
        media.tagName === "AUDIO" &&
        !media.isConnected &&
        !media.loop &&
        (media.currentSrc || media.src || "").startsWith(
            "https://static.whatsapp.net/"
        );

    const originalPlay = HTMLMediaElement.prototype.play;
    HTMLMediaElement.prototype.play = function (...args) {
        if (state.suppressed && isMessageTone(this)) {
            return Promise.resolve();
        }
        return originalPlay.apply(this, args);
    };
})();
