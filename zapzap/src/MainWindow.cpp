#include "MainWindow.h"
#include <QWebEngineView>
#include <QUrl>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    browser = new QWebEngineView(this);
    browser->setUrl(QUrl("https://web.whatsapp.com"));

    setCentralWidget(browser);
    resize(1024, 768);
}
