import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtWebEngine

ApplicationWindow {
    id: root
    width: 1200
    height: 760
    visible: true
    title: "ZapZap"

    WebEngineProfile {
        id: zapzapProfile
        offTheRecord: false
        storageName: "zapzap-qml"
        persistentStoragePath: webEngineConfig.persistentStoragePath
        cachePath: webEngineConfig.cachePath
        persistentCookiesPolicy: WebEngineProfile.ForcePersistentCookies
        httpUserAgent: webEngineConfig.userAgent
    }

    header: ToolBar {
        RowLayout {
            anchors.fill: parent
            anchors.margins: 12

            Label {
                text: "ZapZap"
                font.pixelSize: 20
                font.bold: true
            }

            Item { Layout.fillWidth: true }

            Label {
                text: qsTr("QML experimental")
                opacity: 0.75
            }
        }
    }

    WebEngineView {
        id: webview
        objectName: "zapzapWebView"
        anchors.fill: parent
        profile: zapzapProfile
        url: webEngineConfig.whatsappUrl
    }
}
