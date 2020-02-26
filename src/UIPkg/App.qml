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

            CButton { id: startBtn; text: "Start"; onClicked: { backend.startAcquisition(); mainLayout.disableMainLayout() } }
            CButton { id: stopBtn; text: "Stop"; onClicked: { backend.stopAcquisition(); mainLayout.enableMainLayout() } }
        }

        TabBar {
            id: bar
            Layout.preferredWidth: parent.width

            TabButton { text: "Camera Preview"; width: implicitWidth; contentItem: CCenteredText {} }
            TabButton { text: "Engine Configuration"; width: implicitWidth; contentItem: CCenteredText {} }
        }

        StackLayout {
            id: mainLayout
            Layout.preferredWidth: parent.width
            currentIndex: bar.currentIndex

            enabled: backend.mainLayoutEnabled
            opacity: enabled ? 1 : 0.3

            function enableMainLayout() {
                backend.setMainLayout(true)
            }

            function disableMainLayout() {
                backend.setMainLayout(false)
            }

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

