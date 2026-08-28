"""D-Bus Control interface for ZapZap - permite controlar ZapZap desde el sistema.

Expone com.rtosta.zapzap.Control en /com/rtosta/zapzap con métodos:
 - OpenChat(phone) -> abre chat por número (usa build_open_chat_url)
 - SendMessage(text) -> escribe y envía en el chat activo
 - OpenChatWithMessage(phone, text) -> abre chat y envía (con delay)
 - Status() -> JSON con cuentas y estado
 - Ping() -> pong

También se usa via QLocalServer JSON fallback para AppImage sin D-Bus.
"""

from __future__ import annotations

import json
import logging
import urllib.parse

from PyQt6.QtCore import QObject, pyqtClassInfo, pyqtSlot, QTimer, QUrl
from PyQt6.QtDBus import QDBusAbstractAdaptor, QDBusConnection

from zapzap import __desktopid__
import zapzap
from zapzap.features.browser.web.open_chat import ChatTarget, validate_chat_target, build_open_chat_url
from zapzap.features.browser.web.deeplink import build_open_chat_script

logger = logging.getLogger(__name__)


def _find_input_js() -> str:
    """JS snippet helpers - not executed here, just for reference."""
    return ""


SEND_MESSAGE_JS_TEMPLATE = r"""
(function(text) {{
    try {{
        function findInput() {{
            // Lexical editor (WA 2024+) es el más fiable
            return document.querySelector('div[data-lexical-editor="true"]')
                || document.querySelector('div[contenteditable="true"][data-tab="10"]')
                || document.querySelector('div[contenteditable="true"][data-tab="9"]')
                || document.querySelector('footer div[contenteditable="true"]')
                || document.querySelector('[data-testid="conversation-compose-box-input"]')
                || document.querySelector('div[role="textbox"]');
        }}
        function findSendButton() {{
            return document.querySelector('footer button[aria-label="Enviar"]')
                || document.querySelector('footer button[aria-label="Send"]')
                || document.querySelector('span[data-icon="wds-ic-send-filled"]')
                || document.querySelector('span[data-icon="send"]')
                || document.querySelector('[data-testid="send"]')
                || document.querySelector('button[data-testid="compose-btn-send"]');
        }}
        function findLexicalP(input) {{
            if (!input) return null;
            if (input.tagName === 'P') return input;
            return input.querySelector('p');
        }}
        let input = findInput();
        if (!input) return "ERR: no input found - chat not open yet? url="+location.href;
        input.focus();
        // Lexical: el contenido real está en <p> dentro del div lexical
        let isLexical = input.hasAttribute('data-lexical-editor') || !!document.querySelector('div[data-lexical-editor="true"]');
        let p = findLexicalP(input);
        if (isLexical && p) {{
            // método lexical: set textContent en <p> y dispara beforeinput/input
            // limpia primero
            p.textContent = "";
            // inserta via lexical span
            let span = document.createElement('span');
            span.setAttribute('data-lexical-text', 'true');
            span.textContent = text;
            span.className = 'selectable-text copyable-text xkrh14z';
            p.appendChild(span);
            // dispara eventos que lexical escucha
            try {{ input.dispatchEvent(new InputEvent('beforeinput', {{bubbles:true, cancelable:true, inputType:'insertText', data:text}})); }} catch(e){{}}
            input.dispatchEvent(new InputEvent('input', {{bubbles:true, data:text, inputType:'insertText'}}));
            input.dispatchEvent(new Event('change', {{bubbles:true}}));
            // fuerza actualización de composición
            input.dispatchEvent(new CompositionEvent('compositionend', {{bubbles:true, data:text}}));
        }} else {{
            // fallback viejo (contenteditable simple)
            let ok = false;
            try {{ document.execCommand('insertText', false, text); ok = true; }} catch(e) {{}}
            if (!ok) {{ input.textContent = text; }}
            input.dispatchEvent(new InputEvent('input', {{bubbles:true}}));
            input.dispatchEvent(new Event('change', {{bubbles:true}}));
        }}

        // espera a que WA habilite el botón (lexical es async)
        let attempts = 0;
        let trySend = function() {{
            attempts++;
            let btn = findSendButton();
            if (btn) {{
                let b = btn.closest('button') || btn;
                if (b) {{ b.click(); return; }}
            }}
            if (attempts < 12) {{
                setTimeout(trySend, 200);
            }} else {{
                // fallback Enter si nunca apareció botón
                let enterOpts = {{key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true, cancelable:true}};
                try {{ input.dispatchEvent(new KeyboardEvent('keydown', enterOpts)); }} catch(e){{}}
                try {{ input.dispatchEvent(new KeyboardEvent('keypress', enterOpts)); }} catch(e){{}}
                try {{ input.dispatchEvent(new KeyboardEvent('keyup', {{key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true}})); }} catch(e){{}}
                if (p) {{ try {{ p.dispatchEvent(new KeyboardEvent('keydown', enterOpts)); }} catch(e){{}} }}
                document.dispatchEvent(new KeyboardEvent('keydown', enterOpts));
            }}
        }};
        setTimeout(trySend, 600);
        return "OK: queued lexical send '" + text.substring(0,40) + "' lexical="+isLexical;
    }} catch(e) {{
        return "ERR: " + e.message + " " + e.stack;
    }}
}})(%s)
"""


@pyqtClassInfo("D-Bus Interface", "com.rtosta.zapzap.Control")
class ZapZapControlAdaptor(QDBusAbstractAdaptor):
    def __init__(self, parent: QObject, controller):
        super().__init__(parent)
        self._controller = controller  # callable provider: () -> MainWindowController | None

    def _get_window(self):
        try:
            fn = self._controller
            w = fn() if callable(fn) else fn
            return w
        except Exception:
            logger.exception("Control: failed to get window")
            return None

    PREFERRED_ACCOUNT_ID = "storage-whats"  # wid 593979363865:15@c.us - cuenta correcta, no usar 3 (593963066828)

    def _get_page_and_webview(self, preferred_id=None):
        w = self._get_window()
        if w is None:
            return None, None
        try:
            browser = getattr(w, "browser", None)
            if browser is None and hasattr(w, "inner_window"):
                browser = getattr(w.inner_window, "browser", None)
            if browser is None:
                return None, None
            # Preferencia: storage-whats (cuenta correcta por defecto)
            explicit = preferred_id is not None and str(preferred_id) != ""
            pref = preferred_id or self.PREFERRED_ACCOUNT_ID
            account_keys = [pref]
            if isinstance(pref, str) and pref.isdigit():
                account_keys.append(int(pref))
            webview = None
            # intenta primero el preferido por id
            if pref:
                try:
                    # busca via webview_for_user_id o via _accounts
                    for account_key in account_keys:
                        if hasattr(browser, "webview_for_user_id"):
                            cand = browser.webview_for_user_id(account_key)
                            if cand and hasattr(cand, "page"):
                                webview = cand
                        if not webview and hasattr(browser, "_accounts"):
                            rt = browser._accounts.get(account_key)
                            if rt and hasattr(rt, "page") and rt.page:
                                webview = rt.page
                        if webview:
                            break
                except Exception:
                    pass
            if webview is not None and explicit:
                # Cuenta explícita: tráela al frente para operar sobre la página visible.
                self._focus_webview(browser, webview)
            if not webview:
                webview = browser.current_webview()
            # fallback si está en grid view: busca primer runtime activo
            if webview is None:
                try:
                    # intenta _active_runtimes o _last_active_webview
                    candidates = []
                    if hasattr(browser, "_active_runtimes"):
                        candidates = list(browser._active_runtimes())
                    # _active_runtimes retorna runtimes (WebView wrappers)
                    for rt in candidates:
                        # runtime puede ser WebView mismo o objeto con .page
                        cand = getattr(rt, "page", None)
                        # si es WebView, rt es WebView
                        if hasattr(rt, "page") and hasattr(rt.page(), "runJavaScript"):
                            webview = rt
                            break
                        # fallback: rt may be WebView
                    if webview is None and hasattr(browser, "_last_active_webview") and browser._last_active_webview:
                        webview = browser._last_active_webview
                    if webview is None and hasattr(browser, "pages"):
                        # último intento: recorre stack
                        for i in range(browser.pages.count()):
                            widget = browser.pages.widget(i)
                            if hasattr(widget, "page") and hasattr(widget.page(), "runJavaScript"):
                                # verifica que sea WebView con user enable
                                if getattr(getattr(widget, "user", None), "enable", True):
                                    webview = widget
                                    # activa este webview
                                    try:
                                        browser.pages.setCurrentWidget(widget)
                                    except Exception:
                                        pass
                                    break
                except Exception:
                    logger.exception("Control: fallback webview search failed")
            if webview is None:
                return None, None
            page = webview.page()
            if not hasattr(page, "runJavaScript"):
                return None, None
            return page, webview
        except Exception:
            logger.exception("Control: failed to get page")
            return None, None

    def _focus_webview(self, browser, webview):
        """Trae el webview indicado al frente (switch_to_page / setCurrentWidget) para operar sobre su página visible."""
        try:
            if webview is not None and hasattr(browser, "switch_to_page"):
                browser.switch_to_page(webview)
                return
            if hasattr(browser, "pages"):
                pages = browser.pages
                # localiza el índice del widget y lo activa
                widget = webview
                if not hasattr(widget, "user") and hasattr(widget, "page"):
                    widget = webview
                try:
                    pages.setCurrentWidget(widget)
                except Exception:
                    pass
        except Exception:
            logger.exception("Control: failed to focus webview")

    def _get_page(self):
        page, _ = self._get_page_and_webview()
        return page

    def _activate_window(self):
        w = self._get_window()
        if w:
            try:
                # si está en grid, deja que el chat se abra en el webview activo
                w.show()
                w.raise_()
                w.activateWindow()
                # también asegura que el browser no esté en grid oculto
                browser = getattr(w, "browser", None)
                if browser is None and hasattr(w, "inner_window"):
                    browser = getattr(w.inner_window, "browser", None)
                if browser and hasattr(browser, "pages") and browser.pages.currentWidget() == getattr(browser, "grid_view", None):
                    # no forzamos salida de grid, el open_chat_by_number lo hará
                    pass
            except Exception:
                pass

    @pyqtSlot(str, result=str)
    def Ping(self, _unused=""):
        return "pong zapzap " + zapzap.__version__

    @pyqtSlot(result=str)
    def Status(self):
        w = self._get_window()
        if w is None:
            return json.dumps({"ok": False, "error": "no window"})
        try:
            browser = getattr(w, "browser", None)
            if browser is None and hasattr(w, "inner_window"):
                browser = getattr(w.inner_window, "browser", None)
            users = []
            cur = None
            if browser:
                try:
                    # BrowserController stores users
                    if hasattr(browser, "_users"):
                        users = [str(u) for u in browser._users]
                except Exception:
                    pass
                try:
                    cv = browser.current_webview()
                    if cv and hasattr(cv, "user") and cv.user:
                        cur = getattr(cv.user, "name", None) or str(getattr(cv.user, "id", ""))
                except Exception:
                    pass
            return json.dumps({"ok": True, "version": zapzap.__version__, "current": cur, "users": users}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})

    @pyqtSlot(str, result=str)
    def OpenChat(self, phone):
        """phone puede ser 593..., 09..., +593..., o URL wa.me/api.whatsapp.com"""
        phone = (phone or "").strip()
        if not phone:
            return "ERR: empty phone"
        # si es URL, intenta extraer phone y usar open_chat_by_number (más fiable que deeplink)
        if phone.startswith("http") or phone.startswith("whatsapp://"):
            # intenta parsear wa.me / api.whatsapp.com
            try:
                parsed = urllib.parse.urlparse(phone)
                # wa.me/593XXX  o  /send?phone=593XXX
                digits = ""
                if parsed.query:
                    qs = urllib.parse.parse_qs(parsed.query)
                    if "phone" in qs:
                        digits = "".join(c for c in qs["phone"][0] if c.isdigit())
                if not digits:
                    # path como /593979271867
                    path_digits = "".join(c for c in parsed.path if c.isdigit())
                    if path_digits:
                        digits = path_digits
                if digits:
                    return self._open_via_number(digits)
            except Exception:
                pass
            return self._open_via_deeplink(phone)
        # normalizar a digits y usar ChatTarget
        digits = "".join(c for c in phone if c.isdigit())
        if digits.startswith("0") and len(digits) == 10:
            digits = "593" + digits[1:]
        elif len(digits) == 9:
            digits = "593" + digits
        return self._open_via_number(digits)

    @pyqtSlot(str, str, result=str)
    def OpenChatOnAccount(self, phone, account_id):
        """Open a chat on a specific WhatsApp account without changing the default."""
        phone = (phone or "").strip()
        digits = "".join(c for c in phone if c.isdigit())
        if digits.startswith("0") and len(digits) == 10:
            digits = "593" + digits[1:]
        elif len(digits) == 9:
            digits = "593" + digits
        window = self._get_window()
        browser = getattr(window, "browser", None) if window is not None else None
        account_key = int(account_id) if str(account_id).isdigit() else account_id
        if browser is not None and hasattr(browser, "activate_account"):
            browser.activate_account(account_key)
        page, _ = self._get_page_and_webview(account_key)
        if page is None:
            return f"ERR: account {account_id} has no active WebView"
        try:
            return self._open_page_with_target(page, digits)
        except Exception as e:
            return f"ERR: {e}"

    def _open_page_with_target(self, page, digits: str) -> str:
        if digits.startswith("593"):
            target = validate_chat_target("593", digits[3:], "")
            if hasattr(page, "open_chat_by_number"):
                page.open_chat_by_number(target)
                self._activate_window()
                return f"OK: OpenChat via account-specific page {target.normalized_phone}"
        url = f"https://web.whatsapp.com/send?phone={digits}"
        page.setUrl(QUrl(url))
        self._activate_window()
        return f"OK: OpenChat on account queued {url}"

    def _open_via_number(self, digits: str) -> str:
        page, webview = self._get_page_and_webview()
        if page is None:
            return "ERR: no active WebView/page - inicia ZapZap y espera que cargue WA"
        # intenta validar y usar open_chat_by_number (navegación directa web.whatsapp.com/send?phone=)
        try:
            if digits.startswith("593"):
                cc = "593"
                nn = digits[3:]
            else:
                # fallback deeplink wa.me para extranjeros
                return self._open_via_deeplink(f"https://wa.me/{digits}")
            target = validate_chat_target(cc, nn, "")
            # método directo de PageController - más fiable que anchor click
            if hasattr(page, "open_chat_by_number"):
                page.open_chat_by_number(target)
                self._activate_window()
                return f"OK: OpenChat via open_chat_by_number {target.normalized_phone}"
            else:
                url = build_open_chat_url(target)
                return self._open_via_deeplink(url)
        except Exception as e:
            logger.warning("OpenChat _open_via_number failed %s: %s, fallback wa.me", digits, e)
            return self._open_via_deeplink(f"https://wa.me/{digits}")

    def _open_via_deeplink(self, url: str) -> str:
        page, _ = self._get_page_and_webview()
        if page is None:
            return "ERR: no active WebView/page - inicia ZapZap y espera que cargue WA"
        script = build_open_chat_script(url)
        if script is None:
            return f"ERR: URL no permitida por deeplink policy: {url}"
        try:
            page.runJavaScript(script)
            self._activate_window()
            return f"OK: OpenChat queued {url}"
        except Exception as e:
            return f"ERR: {e}"

    @pyqtSlot(str, result=str)
    def SendMessage(self, text):
        text = text or ""
        if not text.strip():
            return "ERR: empty text"
        page, _ = self._get_page_and_webview()
        if page is None:
            return "ERR: no active page"
        # Paso 1: inserta texto lexical
        js_insert = r"""
(function(text){
  try{
    let input = document.querySelector('div[data-lexical-editor="true"]') || document.querySelector('div[contenteditable="true"][data-tab="10"]');
    if(!input) return 'ERR no input';
    input.focus();
    let p = input.querySelector('p');
    if(!p){
      // WA 2026: el editor ya no siempre trae <p> — execCommand insertText
      // funciona sobre el contenteditable directo (verificado 2026-08-28).
      document.execCommand('selectAll', false, null);
      document.execCommand('delete', false, null);
      document.execCommand('insertText', false, text);
      return 'inserted-exec:'+text.substring(0,30);
    }
    p.innerHTML='';
    let s=document.createElement('span');
    s.setAttribute('data-lexical-text','true');
    s.textContent=text;
    s.className='selectable-text copyable-text xkrh14z';
    p.appendChild(s);
    try{ input.dispatchEvent(new InputEvent('beforeinput',{bubbles:true,cancelable:true,inputType:'insertText',data:text})); }catch(e){}
    input.dispatchEvent(new InputEvent('input',{bubbles:true,data:text,inputType:'insertText'}));
    input.dispatchEvent(new Event('change',{bubbles:true}));
    return 'inserted:'+text.substring(0,30);
  }catch(e){ return 'ERR:'+e.message; }
})(%s)
""" % json.dumps(text)
        js_click = r"""
(function(){
  try{
    let btn = document.querySelector('footer button[aria-label="Enviar"]') || document.querySelector('footer button[aria-label="Send"]') || document.querySelector('span[data-icon="wds-ic-send-filled"]') || document.querySelector('[data-testid="send"]') || document.querySelector('span[data-icon="send"]');
    if(!btn) return 'no btn';
    let b = btn.closest('button') || btn;
    b.click();
    return 'clicked';
  }catch(e){ return 'ERR:'+e.message; }
})()
"""
        try:
            def _cb1(r):
                logger.info("SendMessage insert: %s", r)
            def _cb2(r):
                logger.info("SendMessage click: %s", r)
            page.runJavaScript(js_insert, _cb1)
            # click con delay python (más fiable que JS setTimeout)
            QTimer.singleShot(900, lambda: page.runJavaScript(js_click, _cb2))
            return "OK: SendMessage queued (insert + click 900ms)"
        except Exception as e:
            return f"ERR: {e}"

    @pyqtSlot(str, result=str)
    def EvalJS(self, js_code):
        """Ejecuta JS arbitrario y retorna resultado (para debug). Bloquea hasta 2s."""
        return self._eval_js_on_page(js_code, None)

    @pyqtSlot(result=str)
    def DebugInput(self):
        js = r"""
(function(){
  let out = [];
  function test(sel){ try{ let e=document.querySelector(sel); return e ? (e.tagName+":"+sel+" FOUND html="+e.outerHTML.substring(0,200)) : sel+" NOT FOUND"; }catch(e){ return sel+" ERR "+e.message; } }
  out.push(test('div[contenteditable="true"][data-tab="10"]'));
  out.push(test('div[contenteditable="true"][data-tab="9"]'));
  out.push(test('footer div[contenteditable="true"]'));
  out.push(test('[data-testid="conversation-compose-box-input"]'));
  out.push(test('div[role="textbox"]'));
  out.push(test('div[contenteditable="true"]'));
  // cuenta todos contenteditable
  let all = document.querySelectorAll('div[contenteditable="true"]');
  out.push("total contenteditable: "+all.length);
  for(let i=0;i<Math.min(all.length,5);i++){
    let el=all[i]; out.push("  ["+i+"] tab="+(el.getAttribute("data-tab")||"")+" testid="+(el.getAttribute("data-testid")||"")+" role="+(el.getAttribute("role")||"")+" html="+el.outerHTML.substring(0,300));
  }
  // footer
  let foot=document.querySelector('footer');
  out.push("footer: "+(foot?foot.outerHTML.substring(0,500):"NOT FOUND"));
  // url
  out.push("url: "+location.href);
  // body snippet
  out.push("body len: "+document.body.innerHTML.length);
  return out.join("\n");
})()
"""
        return self.EvalJS(js)

    @pyqtSlot(str, str, result=str)
    def OpenChatWithMessage(self, phone, text):
        r1 = self.OpenChat(phone)
        if r1.startswith("ERR"):
            return r1
        if not text or not text.strip():
            return r1
        # delay para que el chat se abra antes de escribir
        def _delayed():
            self.SendMessage(text)
        QTimer.singleShot(1800, _delayed)
        return f"OK: OpenChatWithMessage queued ({r1}) -> send in 1.8s"

    @pyqtSlot(result=str)
    def ListAccounts(self):
        """Lista todas las cuentas ZapZap con su wid/phone si está disponible."""
        w = self._get_window()
        if w is None:
            return json.dumps({"ok": False, "error": "no window"})
        try:
            browser = getattr(w, "browser", None)
            if browser is None and hasattr(w, "inner_window"):
                browser = getattr(w.inner_window, "browser", None)
            if not browser:
                return json.dumps({"ok": False, "error": "no browser"})
            accounts = []
            try:
                import sqlite3
                from zapzap.core.config.database import Database
                conn = sqlite3.connect(Database.DATABASE_FILE)
                cur = conn.cursor()
                cur.execute("SELECT id, name, enable FROM users")
                rows = cur.fetchall()
                conn.close()
                for r in rows:
                    accounts.append({"id": str(r[0]), "name": r[1], "enable": bool(r[2]), "source": "db"})
            except Exception as e:
                accounts.append({"error_db": str(e)})
            try:
                webviews = []
                if hasattr(browser, "_active_runtimes"):
                    for rt in browser._active_runtimes():
                        if hasattr(rt, "page"):
                            webviews.append(rt)
                if hasattr(browser, "pages"):
                    for i in range(browser.pages.count()):
                        wd = browser.pages.widget(i)
                        if hasattr(wd, "page") and wd not in webviews:
                            webviews.append(wd)
                for idx, wv in enumerate(webviews):
                    try:
                        uid = getattr(getattr(wv, "user", None), "id", f"view-{idx}")
                        uname = getattr(getattr(wv, "user", None), "name", "")
                        accounts.append({"webview_id": str(uid), "webview_name": uname, "has_page": True})
                    except Exception:
                        pass
            except Exception as e:
                accounts.append({"error_webviews": str(e)})
            cur = None
            try:
                cv = browser.current_webview()
                if cv and hasattr(cv, "user"):
                    cur = str(getattr(cv.user, "id", ""))
            except Exception:
                pass
            return json.dumps({"ok": True, "accounts": accounts, "current_webview": cur}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})

    @pyqtSlot(str, result=str)
    def GetAccountWid(self, account_id=""):
        """Obtiene last-wid-md del WebView indicado (o current si vacío)."""
        target_page = None
        w = self._get_window()
        if w is None:
            return json.dumps({"ok": False, "error": "no window"})
        try:
            browser = getattr(w, "browser", None)
            if browser is None and hasattr(w, "inner_window"):
                browser = getattr(w.inner_window, "browser", None)
            if not account_id:
                target_page, _ = self._get_page_and_webview()
            else:
                candidates = []
                if hasattr(browser, "_active_runtimes"):
                    candidates = list(browser._active_runtimes())
                for rt in candidates:
                    # rt es AccountRuntime (tiene .page = WebView) o WebView directo
                    try:
                        user_obj = getattr(rt, "user", None)
                        if user_obj is None and hasattr(rt, "page"):
                            # rt es AccountRuntime, user está en rt.user
                            user_obj = getattr(rt, "user", None)
                        uid = str(getattr(user_obj, "id", "")) if user_obj else ""
                    except Exception:
                        uid = ""
                    if uid == str(account_id):
                        # rt.page puede ser WebView o método
                        try:
                            page_candidate = getattr(rt, "page", None)
                            if callable(page_candidate):
                                # WebView.page() -> QWebEnginePage
                                target_page = page_candidate()
                            else:
                                # AccountRuntime.page -> WebView, luego WebView.page()
                                wv = page_candidate
                                if wv and hasattr(wv, "page") and callable(getattr(wv, "page")):
                                    target_page = wv.page()
                                else:
                                    target_page = wv
                            break
                        except Exception:
                            continue
                if not target_page and hasattr(browser, "pages"):
                    for i in range(browser.pages.count()):
                        wd = browser.pages.widget(i)
                        try:
                            uid = str(getattr(getattr(wd, "user", None), "id", ""))
                        except Exception:
                            continue
                        if uid == str(account_id):
                            try:
                                target_page = wd.page() if callable(getattr(wd, "page")) else wd
                            except Exception:
                                target_page = None
                            break
            if not target_page:
                return json.dumps({"ok": False, "error": f"account {account_id} not found"})
            js = r"""
(function(){
  try{
    let wid = localStorage.getItem('last-wid-md') || localStorage.getItem('last-wid') || '';
    let debug = '';
    for(let k in localStorage){ if(k.includes('wid')||k.includes('WA')) debug+=k+':'+String(localStorage.getItem(k)).substring(0,80)+'|'; }
    return JSON.stringify({ok:true, wid:wid, debug:debug.substring(0,1500), url:location.href});
  }catch(e){ return JSON.stringify({ok:false, error:e.message}); }
})()
"""
            from PyQt6.QtCore import QEventLoop, QTimer
            loop = QEventLoop()
            holder = {"value": None}
            def _cb(r):
                holder["value"] = r
                loop.quit()
            target_page.runJavaScript(js, _cb)
            QTimer.singleShot(2000, loop.quit)
            loop.exec()
            return holder["value"] if holder["value"] else json.dumps({"ok": False, "error": "timeout"})
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})

    @pyqtSlot(str, str, result=str)
    def SendMessageTo(self, phone, text):
        return self.OpenChatWithMessage(phone, text)

    @pyqtSlot(int, result=str)
    def ReadMessages(self, limit=20):
        """Lee últimos N mensajes del chat abierto. Retorna JSON."""
        page, _ = self._get_page_and_webview()
        if page is None:
            return json.dumps({"ok": False, "error": "no active page"})
        js = r"""
(function(limit){
  try {
    let selectors = ['[data-testid="msg-container"]', 'div[data-id]', '[data-testid="conversation-panel-messages"] div[data-id]'];
    let containers = [];
    for(let sel of selectors){
      let els = document.querySelectorAll(sel);
      if(els.length>0){ containers = Array.from(els); break; }
    }
    // fallback: busca todos los mensajes por clase selectable-text
    if(containers.length===0){
      containers = Array.from(document.querySelectorAll('div[data-testid="msg-container"]'));
    }
    let out = [];
    let start = Math.max(0, containers.length - limit);
    for(let i=start; i<containers.length; i++){
      let c = containers[i];
      let text = "";
      // busca span con data-lexical o selectable-text
      let inner = c.querySelector('[data-lexical-text="true"], .selectable-text');
      if(inner) text = inner.innerText || inner.textContent || "";
      else text = c.innerText || c.textContent || "";
      text = text.trim().substring(0,500);
      let isFromMe = c.classList.contains('message-out') || !!c.querySelector('[data-testid="msg-container"] .message-out') || c.innerHTML.includes('message-out');
      // alternativa: detecta por posición (WA pone tail-out)
      let timestamp = "";
      let timeEl = c.querySelector('[data-testid="msg-meta"] span, span[data-testid="msg-date"], [class*="copyable-text"][data-pre-plain-text]');
      if(timeEl) timestamp = timeEl.innerText || timeEl.getAttribute('data-pre-plain-text') || "";
      out.push({index:i, text:text, fromMe:isFromMe, html:c.outerHTML.substring(0,400)});
    }
    return JSON.stringify({ok:true, total:containers.length, messages:out, url:location.href});
  } catch(e){ return JSON.stringify({ok:false, error:e.message}); }
})(%s)
""" % limit
        from PyQt6.QtCore import QEventLoop, QTimer
        loop = QEventLoop()
        holder = {"value": None}
        def _cb(r):
            holder["value"] = r
            loop.quit()
        try:
            page.runJavaScript(js, _cb)
            QTimer.singleShot(2000, loop.quit)
            loop.exec()
            return holder["value"] if holder["value"] else json.dumps({"ok": False, "error": "timeout"})
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})

    @pyqtSlot(int, str, result=str)
    def ReadMessagesOnAccount(self, limit=20, account_id=""):
        """Read the active chat from a specific WhatsApp account."""
        page, _ = self._get_page_and_webview(account_id)
        if page is None:
            return json.dumps({"ok": False, "error": f"account {account_id} has no active page"})
        js = r"""
(function(limit){
  try {
    let els = document.querySelectorAll('[data-testid="msg-container"], div[data-id]');
    let out = [], start = Math.max(0, els.length - limit);
    for (let i=start; i<els.length; i++) {
      let c=els[i], inner=c.querySelector('[data-lexical-text="true"], .selectable-text');
      let text=(inner ? (inner.innerText || inner.textContent) : (c.innerText || c.textContent) || '').trim().substring(0,500);
      let fromMe=c.classList.contains('message-out') || c.innerHTML.includes('message-out');
      out.push({index:i,text,fromMe});
    }
    return JSON.stringify({ok:true,total:els.length,messages:out,url:location.href});
  } catch(e) { return JSON.stringify({ok:false,error:e.message}); }
})(%s)
""" % limit
        from PyQt6.QtCore import QEventLoop, QTimer
        loop = QEventLoop(); holder = {"value": None}
        def _cb(r): holder["value"] = r; loop.quit()
        try:
            page.runJavaScript(js, _cb); QTimer.singleShot(2500, loop.quit); loop.exec()
            return holder["value"] or json.dumps({"ok": False, "error": "timeout"})
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})

    @pyqtSlot(result=str)
    def GetChats(self):
        return self._get_chats_on_page(None)

    @pyqtSlot(str, result=str)
    def GetChatsOnAccount(self, account_id=""):
        """Lista chats visibles en el sidebar de una cuenta concreta (account_id='3'=Personal, 'storage-whats'=Edge)."""
        return self._get_chats_on_page(account_id or None)

    def _get_chats_on_page(self, account_id):
        js = r"""
(function(){
  try{
    // Selector robusto de conversaciones del sidebar de WA Web.
    // Una conversación es un cell-frame-container. Excluimos Archivados/Estados/Comunidades
    // de la lista normal (se identifican por título).
    let cells = Array.from(document.querySelectorAll('[data-testid="cell-frame-container"]'));
    let chats = [];
    for(let i=0;i<cells.length;i++){
      let el = cells[i];
      let t = (el.innerText || el.textContent || '').replace(/\s+/g,' ').trim();
      // Título: primer span[title] o el texto antes del preview
      let titleEl = el.querySelector('span[title]') || el.querySelector('div[title]');
      let title = titleEl ? (titleEl.getAttribute('title')||titleEl.innerText||'').trim() : '';
      // error de parsing: usa la primera línea del texto
      if(!title){
        let first = t.split('. ')[0];
        // WA suele poner "TítuloPreview" (título con emoji inicial). Usa el primer token razonable.
        title = first;
      }
      let preview = '';
      let prevEl = el.querySelector('[data-testid="last-msg-preview"]') ||
                   el.querySelector('span[data-testid="last-msg-preview"]') ||
                   el.querySelector('[data-testid="conversation-info-header-chat-title"]');
      // extrae preview: todo menos título y timestamp
      let meta = el.querySelector('[data-testid="last-msg-preview"], span[data-testid="msg-meta"]');
      if(meta) preview = (meta.innerText||meta.textContent||'').trim();
      // timestamp
      let timeEl = el.querySelector('span[data-testid="msg-meta"], [data-testid="time"]');
      let time = timeEl ? (timeEl.getAttribute('data-timestamp')||timeEl.innerText||'').trim() : '';
      // número (si es un contacto no guardado el título es el número)
      let number = isNaN(parseInt(title.replace(/[^\d]/g,''))) ? '' : title;
      chats.push({
        index:i,
        title: title.substring(0,80),
        preview: preview.substring(0,120),
        time: time,
        number: number,
        html: el.outerHTML.substring(0,200)
      });
    }
    // Devuelve TODOS los encontrados (sin límite artificial)
    return JSON.stringify({ok:true, total:chats.length, chats:chats, url:location.href});
  }catch(e){ return JSON.stringify({ok:false, error:e.message}); }
})()
"""
        from PyQt6.QtCore import QEventLoop, QTimer
        loop = QEventLoop()
        holder = {"value": None}
        def _cb(r):
            holder["value"] = r
            loop.quit()
        page, _ = self._get_page_and_webview(account_id)
        if page is None:
            return json.dumps({"ok": False, "error": "no active page"})
        try:
            page.runJavaScript(js, _cb)
            QTimer.singleShot(2500, loop.quit)
            loop.exec()
            return holder["value"] if holder["value"] else json.dumps({"ok": False, "error": "timeout"})
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})

    @pyqtSlot(str, str, result=str)
    def SendMessageOnAccount(self, text, account_id=""):
        """Envía texto en el chat abierto de una cuenta concreta."""
        return self._send_on_account(text, account_id or None)

    def _send_on_account(self, text, account_id):
        if not text or not text.strip():
            return "ERR: empty text"
        page, _ = self._get_page_and_webview(account_id)
        if page is None:
            return "ERR: no active page"
        js_insert = r"""
(function(text){
  try{
    let input = document.querySelector('div[data-lexical-editor="true"]') || document.querySelector('div[contenteditable="true"][data-tab="10"]');
    if(!input) return 'ERR no input';
    input.focus();
    let p = input.querySelector('p');
    if(!p){
      // WA 2026: el editor ya no siempre trae <p> — execCommand insertText
      // funciona sobre el contenteditable directo (verificado 2026-08-28).
      document.execCommand('selectAll', false, null);
      document.execCommand('delete', false, null);
      document.execCommand('insertText', false, text);
      return 'inserted-exec:'+text.substring(0,30);
    }
    p.innerHTML='';
    let s=document.createElement('span');
    s.setAttribute('data-lexical-text','true');
    s.textContent=text;
    s.className='selectable-text copyable-text xkrh14z';
    p.appendChild(s);
    try{ input.dispatchEvent(new InputEvent('beforeinput',{bubbles:true,cancelable:true,inputType:'insertText',data:text})); }catch(e){}
    input.dispatchEvent(new InputEvent('input',{bubbles:true,data:text,inputType:'insertText'}));
    input.dispatchEvent(new Event('change',{bubbles:true}));
    return 'inserted:'+text.substring(0,30);
  }catch(e){ return 'ERR:'+e.message; }
})(%s)
""" % json.dumps(text)
        js_click = r"""
(function(){
  try{
    let btn = document.querySelector('footer button[aria-label="Enviar"]') || document.querySelector('footer button[aria-label="Send"]') || document.querySelector('span[data-icon="wds-ic-send-filled"]') || document.querySelector('[data-testid="send"]') || document.querySelector('span[data-icon="send"]');
    if(!btn) return 'no btn';
    let b = btn.closest('button') || btn;
    b.click();
    return 'clicked';
  }catch(e){ return 'ERR:'+e.message; }
})()
"""
        def _cb1(r):
            logger.info("SendMessageOnAccount insert: %s", r)
        def _cb2(r):
            logger.info("SendMessageOnAccount click: %s", r)
        try:
            page.runJavaScript(js_insert, _cb1)
            QTimer.singleShot(900, lambda: page.runJavaScript(js_click, _cb2))
            return "OK: SendMessageOnAccount queued (insert + click 900ms)"
        except Exception as e:
            return f"ERR: {e}"

    @pyqtSlot(str, str, result=str)
    def EvalJSOnAccount(self, js_code, account_id=""):
        """Ejecuta JS arbitrario en la página de una cuenta concreta."""
        return self._eval_js_on_page(js_code, account_id or None)

    def _eval_js_on_page(self, js_code, account_id):
        page, _ = self._get_page_and_webview(account_id)
        if page is None:
            return "ERR: no active page"
        from PyQt6.QtCore import QEventLoop, QTimer
        loop = QEventLoop()
        holder = {"value": "timeout"}
        def _cb(r):
            holder["value"] = r
            loop.quit()
        try:
            page.runJavaScript(js_code, _cb)
            QTimer.singleShot(2000, loop.quit)
            loop.exec()
            return json.dumps(holder["value"], ensure_ascii=False)[:4000]
        except Exception as e:
            return f"ERR: {e}"


class ZapZapControlDBus(QObject):
    """Owner de com.rtosta.zapzap.Control en el bus de sesión."""

    def __init__(self, app, window_provider, parent=None):
        super().__init__(parent or app)
        self._app = app
        self._window_provider = window_provider
        self._bus = QDBusConnection.sessionBus()
        self._registered_service = False
        self._registered_object = False
        self._object_path = "/com/rtosta/zapzap"
        self.adaptor = ZapZapControlAdaptor(self, window_provider)

    def start(self) -> bool:
        # intenta own el nombre, pero si ya está tomado (Flatpak D-Bus anterior) igual exporta objeto
        svc = self._bus.registerService(__desktopid__)
        if svc:
            self._registered_service = True
        else:
            # service already owned (ok - we share it with DesktopApplicationDBus)
            logger.warning("Control D-Bus: could not own %s (already owned), will still export object", __desktopid__)
        self._registered_object = self._bus.registerObject(
            self._object_path, self, QDBusConnection.RegisterOption.ExportAdaptors
        )
        if not self._registered_object:
            logger.warning("Control D-Bus: could not export %s", self._object_path)
            if self._registered_service:
                self._bus.unregisterService(__desktopid__)
                self._registered_service = False
            return False
        logger.info("Control D-Bus: exported com.rtosta.zapzap.Control at %s (service owned=%s)", self._object_path, self._registered_service)
        return True

    def stop(self):
        if self._registered_object:
            self._bus.unregisterObject(self._object_path)
            self._registered_object = False
        if self._registered_service:
            self._bus.unregisterService(__desktopid__)
            self._registered_service = False
