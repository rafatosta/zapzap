#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>

class QWidget;

#ifdef HAVE_QTWEBENGINEWIDGETS
class QWebEnginePage;
class QWebEngineProfile;
class QWebEngineView;
#endif

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);

private:
    QWidget *content;

#ifdef HAVE_QTWEBENGINEWIDGETS
    QWebEngineProfile *profile;
    QWebEnginePage *page;
    QWebEngineView *browser;
#endif
};

#endif
