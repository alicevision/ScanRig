import QtQuick 2.0
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.14
import "Components"

ApplicationWindow {
    title: qsTr("ScanRig App")
    visible: true
    height: 800
    width: 800 * 1.7

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

            CButton { 
                id: startBtn
                text: "Start"
                enabled: backend.mainLayoutEnabled && backend.readyForAcquisitionProperty
                onClicked: { mainLayout.disableMainLayout(backend.startAcquisition()) } 
            }
            CButton { 
                id: stopBtn
                text: "Stop"
                enabled: !backend.mainLayoutEnabled
                onClicked: { mainLayout.enableMainLayout(backend.stopAcquisition()) } 
            }
        }

        TabBar {
            id: bar
            Layout.preferredWidth: parent.width

            TabButton { text: "Camera Preview"; width: implicitWidth; contentItem: CCenteredText {} }
            TabButton { text: "Multicamera View"; width: implicitWidth; contentItem: CCenteredText {} }
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

                Layout.preferredHeight: parent.height*0.8
                Layout.fillHeight: true
            }

            // Loader {
            //     source: "Views/MultiCamera.qml"

            //     Layout.preferredHeight: parent.height*0.9
            //     Layout.fillHeight: true
            // }
        }

        Item {
            id: loadingBarAcquisition
            enabled: !backend.mainLayoutEnabled
            visible: !backend.mainLayoutEnabled
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredHeight: 20

            Rectangle {
                anchors.fill: parent
                color: palette.highlight
                border.width: 2
                border.color: palette.window
            }
            CCenteredText { 
                text: "Acquisition in progress: " + acquisition.nbTakenImagesProp + "/" + acquisition.nbImagesToTakeProp + "  | More information in the terminal."
                font: font.family 
            }
        }
    }

}
