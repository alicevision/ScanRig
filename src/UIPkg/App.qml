import QtQuick 2.0
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.14
import "Components"

ApplicationWindow {
    title: qsTr("ScanRig App")
    visible: true
    height: 900
    width: 900 * 1.7

    minimumHeight: 700
    minimumWidth: minimumHeight * 1.7

    maximumHeight: 900
    maximumWidth: maximumHeight * 1.7

    onClosing: {
        close.accepted = backend.exitApplication()
    }

    ColumnLayout {
        anchors.fill: parent

        RowLayout {
            Layout.preferredWidth: startBtn.implicitWidth + stopBtn.implicitWidth
            Layout.topMargin: 10
            Layout.alignment: Qt.AlignCenter

            CButton { id: startBtn; text: "Start"; onClicked: { mainLayout.disableMainLayout(backend.startAcquisition()) } }
            CButton { id: stopBtn; text: "Stop"; onClicked: { mainLayout.enableMainLayout(backend.stopAcquisition()) } }
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

            function enableMainLayout(b) {
                if(b) { backend.setMainLayout(true) }
            }

            function disableMainLayout(b) {
                if(b) { backend.setMainLayout(false) }
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

