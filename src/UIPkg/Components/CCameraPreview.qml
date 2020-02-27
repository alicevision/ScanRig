import QtQuick 2.14
import QtQuick.Layouts 1.14
import QtQuick.Controls 2.14
import QtQuick.Controls.Styles 1.4

GroupBox {
    title: qsTr("Camera Preview")
    
    ColumnLayout {
        anchors.fill: parent
        
        /***** PREVIEW *****/
        Image {
            id: image
            property bool backBuffer: false
            property int camId: -1
            source: "no_device_selected.png"

            asynchronous: false

            fillMode: Image.PreserveAspectFit
            Layout.preferredWidth: parent.width
            Layout.preferredHeight: parent.width / (image.sourceSize.width/image.sourceSize.height)
            Layout.alignment: Qt.AlignTop

            function reload() {
                if(camId != -1 && preview.getRunningPreview()) {
                    backBuffer = !backBuffer
                    image.source = "image://imageProvider/" + camId + "/" + backBuffer
                }
            }

            Timer {
                interval: 40; running: true; repeat: true
                onTriggered: image.reload()
            }
        }

        /***** SETTINGS *****/
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Label {
                text: "Camera:"
            }

            ComboBox {
                Layout.fillWidth: true
                Layout.preferredHeight: 25
                contentItem: CCenteredText { text: parent.displayText }

                // Creating the list with the string "No device selected"
                model: ListModel {
                    id: availableDevicesList

                    ListElement {
                        text: "No Device Selected"
                    }
                }

                // Using JS to add the AvailableDevices to the list
                Component.onCompleted: {
                    // availableDevices is a list which comes from Python
                    for(let camIndex in availableUvcCameras) {
                        availableDevicesList.append({text: camIndex.toString()})
                    }
                }

                onActivated: {
                    // If index == 0 because the first element is the string "No Device Selected"
                    if (currentIndex == 0) {
                        preview.changePreview(-1)
                        image.camId = -1
                        image.source = "no_device_selected.png"
                    }
                    else if (parseInt(currentText) == image.camId) {
                        return
                    }
                    else {
                        preview.changePreview(parseInt(currentText))
                        image.camId = parseInt(currentText)
                    }
                    acquisitionListBtn.refreshText()
                }
            }

            Label {
                text: "Preview Quality:"
            }

            ComboBox {
                Layout.preferredHeight: 25
                Layout.preferredWidth: 75
                contentItem: CCenteredText { text: parent.displayText }

                model: ["Full", "1/2", "1/4"]
                onActivated: {
                }
            }
        }

        CButton { 
            id: acquisitionListBtn
            text: ""
            Layout.alignment: Qt.AlignCenter

            Component.onCompleted: refreshText()

            onClicked: {
                preview.addRemoveDeviceToAcquisition()
                acquisitionListBtn.refreshText()
            }

            function refreshText() {
                if(image.camId == -1) {
                    acquisitionListBtn.enabled = false
                    acquisitionListBtn.text = ""
                }
                else {
                    acquisitionListBtn.enabled = true
                    acquisitionListBtn.text = preview.isCurrentDeviceInAcquisition() ? "Remove this camera from the Acquisition process !" : "Add this camera to the Acquisition process !"
                }
            }
        }
    }
}