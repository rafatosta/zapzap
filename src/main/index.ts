import { app, shell, BrowserWindow, ipcMain, Tray, Menu, MenuItem, nativeImage } from 'electron'
import { join } from 'path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import icon from '../../resources/icon.png?asset'

let mainWindow: BrowserWindow | null = null;
let tray: Tray | null = null;
let isQuitting = false;


// Single Electron Instance
if (!app.requestSingleInstanceLock()) {
	app.quit()
}

function createWindow(): void {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 900,
    height: 670,
    show: false,
    autoHideMenuBar: false,
    ...(process.platform === 'linux' ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false,
      webviewTag: true
    }
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow?.show()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow?.hide();
    }
  })

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

function createTray(): void {
  const trayIcon = nativeImage.createFromPath(icon)
  tray = new Tray(trayIcon)

  // Criar referência para o menu item Show/Hide
  const toggleVisibilityItem = new MenuItem({
    label: mainWindow?.isVisible() ? 'Hide' : 'Show',
    click: () => {
      if (!mainWindow) return

      if (mainWindow.isVisible()) {
        mainWindow.hide()
      } else {
        mainWindow.show()
      }

      updateTrayMenu()
    }
  })

  const contextMenu = Menu.buildFromTemplate([
    toggleVisibilityItem,
    { type: 'separator' },
    {
      label: 'Quit',
      accelerator: 'CmdOrCtrl+Q',
      click: () => {
        isQuitting = true;
        app.quit();
      }
    }
  ])

  function updateTrayMenu(): void {
    toggleVisibilityItem.label = mainWindow?.isVisible() ? 'Hide' : 'Show'
    tray?.setContextMenu(Menu.buildFromTemplate([
      toggleVisibilityItem,
      { type: 'separator' },
      {
        label: 'Quit',
        accelerator: 'CmdOrCtrl+Q',
        click: () => app.quit()
      }
    ]))
  }

  tray.setToolTip('Meu App Electron')
  tray.setContextMenu(contextMenu)

  tray.on('click', () => {
    if (!mainWindow) return

    if (mainWindow.isVisible()) {
      mainWindow.hide()
    } else {
      mainWindow.show()
    }

    updateTrayMenu()
  })

  // Atualiza o menu sempre que a janela for escondida ou mostrada por outros meios
  mainWindow?.on('show', updateTrayMenu)
  mainWindow?.on('hide', updateTrayMenu)
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  // Set app user model id for windows
  electronApp.setAppUserModelId('com.electron')

  // Default open or close DevTools by F12 in development
  // and ignore CommandOrControl + R in production.
  // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  // IPC test
  ipcMain.on('ping', () => console.log('pong'))

  createWindow()
  createTray()

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', () => {
  isQuitting = true;
});

app.on('second-instance', () => {
  const hide = false
	if (!mainWindow?.isFocused()) {
			if (mainWindow?.isVisible()) {
				mainWindow?.focus();
			}
			else if (mainWindow?.isMinimized()) {
				mainWindow?.restore();
				mainWindow?.focus();
			}
			else {
				mainWindow?.show();
				mainWindow?.restore();
				mainWindow?.focus();
			}
		}
		else {
			if (hide) {
				mainWindow?.hide();
			}
		}
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
