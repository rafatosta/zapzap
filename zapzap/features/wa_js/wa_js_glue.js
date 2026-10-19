(function () {
  "use strict";
  function notifyReady() {
    try {
      if (window.zapzapWaJsBridge && typeof window.zapzapWaJsBridge.on_ready === "function") {
        window.zapzapWaJsBridge.on_ready();
      }
    } catch (e) {}
  }
  function callWpp(callbackId, path, args) {
    try {
      const parts = String(path).split(".");
      let fn = window.WPP;
      for (const part of parts) {
        if (!fn || typeof fn[part] === "undefined") { throw new Error("WPP." + path + " is unavailable"); }
        fn = fn[part];
      }
      if (typeof fn !== "function") { throw new Error("WPP." + path + " is not a function"); }
      const result = fn.apply(null, Array.isArray(args) ? args : []);
      let serialized = null;
      try { serialized = JSON.stringify(result); } catch (e) { serialized = JSON.stringify({ ok: true }); }
      if (window.zapzapWaJsBridge && typeof window.zapzapWaJsBridge.on_result === "function") {
        window.zapzapWaJsBridge.on_result(callbackId, serialized || "null");
      }
    } catch (e) {
      if (window.zapzapWaJsBridge && typeof window.zapzapWaJsBridge.on_error === "function") {
        window.zapzapWaJsBridge.on_error(callbackId, String(e && e.message ? e.message : e));
      }
    }
  }
  window.zapzapWaJs = { call: callWpp };
  function waitForWpp() {
    if (window.WPP && window.WPP.isReady) { notifyReady(); return; }
    setTimeout(waitForWpp, 500);
  }
  waitForWpp();
})();
