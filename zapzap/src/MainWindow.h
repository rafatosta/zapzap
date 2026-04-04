#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>

class QWebEngineView;

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);

private:
    QWebEngineView *browser;
};

#endif
