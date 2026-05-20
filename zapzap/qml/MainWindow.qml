import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    width: 1200
    height: 760
    visible: true
    title: "ZapZap"

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

            Button {
                text: qsTr("Configurações")
                enabled: false
                ToolTip.visible: hovered
                ToolTip.text: qsTr("Em migração para QML")
            }
        }
    }

    Rectangle {
        anchors.fill: parent
        color: palette.window

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 10

            Label {
                Layout.alignment: Qt.AlignHCenter
                text: qsTr("Migração para QML iniciada")
                font.pixelSize: 28
                font.bold: true
            }

            Label {
                Layout.alignment: Qt.AlignHCenter
                text: qsTr("A estrutura base em QML foi criada para substituir a UI em .ui gradualmente.")
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
                Layout.maximumWidth: 640
            }
        }
    }
}
