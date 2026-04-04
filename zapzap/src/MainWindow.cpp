#include "MainWindow.h"

#ifdef HAVE_QTWEBENGINEWIDGETS
#include <QDir>
#include <QStandardPaths>
#include <QUrl>
#include <QWebEnginePage>
#include <QWebEngineProfile>
#include <QWebEngineSettings>
#include <QWebEngineView>
#else
#include <QLabel>
#endif

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
#ifdef HAVE_QTWEBENGINEWIDGETS
    browser = new QWebEngineView(this);

    profile = new QWebEngineProfile("zapzap", this);

    const QString appDataPath = QStandardPaths::writableLocation(QStandardPaths::AppDataLocation);
    const QString webEngineBasePath = appDataPath + "/webengine";
    const QString storagePath = webEngineBasePath + "/storage";
    const QString cachePath = webEngineBasePath + "/cache";

    QDir().mkpath(storagePath);
    QDir().mkpath(cachePath);

    profile->setPersistentStoragePath(storagePath);
    profile->setCachePath(cachePath);
    profile->setHttpCacheType(QWebEngineProfile::DiskHttpCache);
    profile->setPersistentCookiesPolicy(QWebEngineProfile::ForcePersistentCookies);
    profile->settings()->setAttribute(QWebEngineSettings::ForceDarkMode, true);

    QString userAgent = qEnvironmentVariable("ZAPZAP_USER_AGENT");
    if (userAgent.isEmpty()) {
        userAgent =
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36 ZapZap/1.0";
    }
    profile->setHttpUserAgent(userAgent);

    page = new QWebEnginePage(profile, browser);
    browser->setPage(page);
    page->setUrl(QUrl("https://web.whatsapp.com"));

    content = browser;
#else
    auto *label = new QLabel(
        "Qt WebEngineWidgets is not available in this environment.\n"
        "Install Qt WebEngine to enable WhatsApp Web embedding.",
        this
    );
    label->setAlignment(Qt::AlignCenter);
    label->setWordWrap(true);
    content = label;
#endif

    setCentralWidget(content);
    resize(1024, 768);
}
