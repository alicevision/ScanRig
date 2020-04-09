import QtQuick 2.14
import QtQuick.Layouts 1.14
import QtQuick.Controls 2.14
import QtQuick.Controls.Styles 1.4

GroupBox {
    title: qsTr("Camera Preview - Streaming API : " + backend.streamingAPIName)
    id: root
    signal changedAcquisition()
    signal changedDevice()

    function changeTimer() {
        timer.running = !timer.running
    }

    ColumnLayout {
        anchors.fill: parent

        /***** PREVIEW *****/
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredHeight: parent.height - 60

            Image {
                id: image
                property bool backBuffer: false
                property int camId: preview.currentIdProperty
                source: "no_device_selected.png"

                asynchronous: false

                fillMode: Image.PreserveAspectFit
                height: parent.height
                width: parent.width
                Layout.alignment: Qt.AlignCenter

                function reload() {
                    if(camId != -1 && preview.getRunningPreview()) {
                        backBuffer = !backBuffer
                        image.source = "image://imageProvider/" + camId + "/" + backBuffer
                    }
                }

                Timer {
                    id: timer
                    interval: 40; running: true; repeat: true
                    onTriggered: image.reload()
                }
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
                    for(let uvcCamIndex in preview.getAvailableOpencvCameras()) {
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
                        image.source = "no_device_selected.png"
                    }
                    else if (camera === image.camId) {
                        return
                    }
                    else {
                        preview.changePreview(camera)
                    }
                    acquisitionListBtn.refreshText()
                    draftResolution.updateResolutionsList()
                    root.changedDevice()
                }
            }

            Label {
                text: "Preview Quality:"
            }

            ComboBox {
                id: draftResolution
                Layout.preferredHeight: 25
                Layout.preferredWidth: 100
                displayText: preview.cameraFormat
                contentItem: CCenteredText { text: parent.displayText }

                model: ListModel {
                    id: availableResolutionsList
                }

                // Using JS to add the availableResolutions to the list
                Component.onCompleted: {
                    updateResolutionsList()
                }

                onActivated: {
                    preview.setCameraFormat(currentText)
                }

                function updateResolutionsList() {
                    availableResolutionsList.clear()
                    const resolutions = preview.getAvailableUvcResolutions()

                    for(let i = 0; i < resolutions.length; ++i) {
                        const txt = resolutions[i].toString()
                        availableResolutionsList.append({text: txt})
                    }               
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

                if(preview.getDevicesInAcquisition().length > 0) backend.setReadyForAcquisition(true)
                else backend.setReadyForAcquisition(false)
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