#include "MainWindow.h"

#ifdef HAVE_QTWEBENGINEWIDGETS
#include <QWebEngineView>
#include <QUrl>
#else
#include <QLabel>
#endif

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
#ifdef HAVE_QTWEBENGINEWIDGETS
    auto *browser = new QWebEngineView(this);
    browser->setUrl(QUrl("https://web.whatsapp.com"));
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
