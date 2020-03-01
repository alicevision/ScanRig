import QtQuick 2.14
import QtQuick.Layouts 1.14
import QtQuick.Controls 2.14
import QtQuick.Controls.Styles 1.4

GroupBox {
    title: qsTr("Camera Preview")
    id: root
    signal changedAcquisition()

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
            Layout.fillHeight: true
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
                    for(let uvcCamIndex in availableUvcCameras) {
                        const txt = "UVC: " + uvcCamIndex.toString()
                        availableDevicesList.append({text: txt})
                    }
                }

                onActivated: {
                    const txt = currentText
                    let camera;
                    if(txt.startsWith("UVC:")) {
                        camera = parseInt(txt.split("UVC: ")[1])
                    }


                    if (txt === "No Device Selected") {
                        preview.changePreview(-1)
                        image.camId = -1
                        image.source = "no_device_selected.png"
                    }
                    else if (camera === image.camId) {
                        return
                    }
                    else {
                        preview.changePreview(camera)
                        image.camId = camera
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
                root.changedAcquisition()
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