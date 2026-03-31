// WebRTC IP-Leak Prevention Shim
// Replaces host/srflx ICE candidates with 0.0.0.0 to prevent real IP leaks,
// but leaves relay candidates intact so calls can still operate through TURN servers.

(function() {
    const originalRTCPeerConnection = window.RTCPeerConnection || window.webkitRTCPeerConnection;
    if (!originalRTCPeerConnection) return;

    const patchedRTCPeerConnection = function(...args) {
        const pc = new originalRTCPeerConnection(...args);

        const originalAddIceCandidate = pc.addIceCandidate;
        pc.addIceCandidate = function(candidate, successCallback, failureCallback) {
            if (candidate && candidate.candidate) {
                // Obfuscate host/srflx candidates (local network / direct public IP)
                if (candidate.candidate.includes('typ host') || candidate.candidate.includes('typ srflx')) {
                    candidate.candidate = candidate.candidate.replace(/([0-9]{1,3}\.){3}[0-9]{1,3}/g, '0.0.0.0');
                    candidate.candidate = candidate.candidate.replace(/[0-9a-fA-F]{1,4}(:[0-9a-fA-F]{0,4}){2,7}/g, '::');
                }
            }
            if (arguments.length > 1) {
                return originalAddIceCandidate.apply(this, arguments);
            } else {
                return originalAddIceCandidate.call(this, candidate)
                    .then(successCallback)
                    .catch(failureCallback);
            }
        };

        const originalCreateOffer = pc.createOffer;
        pc.createOffer = function() {
            return originalCreateOffer.apply(this, arguments);
        };

        const originalCreateAnswer = pc.createAnswer;
        pc.createAnswer = function() {
             return originalCreateAnswer.apply(this, arguments);
        };

        return pc;
    };

    patchedRTCPeerConnection.prototype = originalRTCPeerConnection.prototype;
    
    // Some properties might be read-only, we try to overwrite them
    try {
        window.RTCPeerConnection = patchedRTCPeerConnection;
    } catch(e) {}
    try {
        window.webkitRTCPeerConnection = patchedRTCPeerConnection;
    } catch(e) {}

    console.log("ZapZap WebRTC Shield activated.");
})();
