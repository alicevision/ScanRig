import QtQuick 2.0
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.14
import "Components"

ApplicationWindow {
    title: qsTr("ScanRig App")
    visible: true
    width: 960
    height: 700

    ColumnLayout {
        anchors.fill: parent

        Flow {
            spacing: 2

            CButton {
                text: "Stop"
            }

            CButton {
                text: "Start"
            }
        }

        TabBar {
            id: bar
            width: parent.width

            TabButton {
                text: "Camera Preview"
                width: implicitWidth
            }

            TabButton {
                text: "Engine Configuration"
                width: implicitWidth
            }

        }

        StackLayout {
            width: parent.width
            currentIndex: bar.currentIndex

            Loader {
                source: "Views/Preview.qml"

                Layout.preferredHeight: parent.height*0.9
                Layout.fillHeight: true
            }

            Loader {
                source: "Views/Capture.qml"

                Layout.preferredHeight: parent.height*0.9
                Layout.fillHeight: true
            }
        }
    }

}

