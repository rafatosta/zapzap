// Extension made by github/migliorelli
// https://github.com/migliorelli/whatsappweb-message-ctx

async function waitWhatsapp() {
    const selector = "div:has(> div#main)"

    return new Promise(resolve => {
        if (document.querySelector(selector)) {
            return resolve(document.querySelector(selector))
        }

        const observer = new MutationObserver(() => {
            if (document.querySelector(selector)) {
                observer.disconnect()
                return resolve(document.querySelector(selector))
            }
        })

        observer.observe(document.body, {
            childList: true, subtree: true
        })
    })
}

function getMessages() {
    const selector = "div.message-in > div, div.message-out > div"
    return document.querySelectorAll(selector)
}

function bindContextMenuEvent(element) {
    const wasBinded = element.getAttribute('data-context-menu-bound')
    if (wasBinded) {
        return
    }

    let lastClick = Date.now()
    element.addEventListener('contextmenu', (event) => {
        const currentTime = Date.now()
        const delay = currentTime - lastClick
        lastClick = currentTime

        if (delay < 500) {
            return
        }

        event.preventDefault()
        const contextMenuButton = document.querySelector('[aria-label="Context menu"]')
        if (contextMenuButton) {
            contextMenuButton.click()
        }
    })

    element.addEventListener('doubleclick', () => {
        element.click()
    })

    element.setAttribute('data-context-menu-bound', 'true')
}

async function main() {
    const main = await waitWhatsapp()

    if (!main) {
        console.error('[ContextMenuAddon]: WhatsApp not ready')
        return
    }

    const observer = new MutationObserver(() => {
        const messages = getMessages()
        if (messages.length <= 0) return

        for (let message of messages) {
            bindContextMenuEvent(message)
        }
    })

    observer.observe(main, {
        childList: true, subtree: true
    })
}

main().then(() => {
    console.error('[ContextMenuAddon]: WhatsApp context menu addon initialized')
})
