import QtQuick 2.0
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.14
import "Components"

ApplicationWindow {
    title: qsTr("ScanRig App")
    visible: true
    width: 1500
    height: 900

    onClosing: {
        backend.exitApplication()
        close.accepted = true
    }

    ColumnLayout {
        anchors.fill: parent

        RowLayout {
            Layout.preferredWidth: startBtn.implicitWidth + stopBtn.implicitWidth
            Layout.topMargin: 10
            Layout.alignment: Qt.AlignCenter

            CButton { id: startBtn; text: "Start"; onClicked: backend.startAcquisition() }
            CButton { id: stopBtn; text: "Stop" }
        }

        TabBar {
            id: bar
            Layout.preferredWidth: parent.width

            TabButton { text: "Camera Preview"; width: implicitWidth }
            TabButton { text: "Engine Configuration"; width: implicitWidth }
        }

        StackLayout {
            Layout.preferredWidth: parent.width
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

