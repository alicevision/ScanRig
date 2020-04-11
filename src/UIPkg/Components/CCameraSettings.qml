import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14
import Qt.labs.platform 1.1

GroupBox {
    title: qsTr("Camera Settings")
    id: root
    signal dialog()
    property alias res : resolutionComboBox

    ColumnLayout {
        spacing: 10

        RowLayout {
            Layout.fillWidth: true

            Label {
                text: "Resolution"
                horizontalAlignment: Text.AlignRight
                Layout.preferredWidth: exposure.labelSize
            }

            ComboBox {
                id: resolutionComboBox
                Layout.preferredHeight: 25
                Layout.preferredWidth: 150
                displayText: preview.cameraAcquisitionFormat
                contentItem: CCenteredText { text: parent.displayText }

                model: ListModel {
                    id: availableResolutionsList
                }

                // Using JS to add the availableResolutions to the list
                Component.onCompleted: {
                    updateResolutionsList()
                }

                onActivated: {
                    preview.setCameraAcquisitionFormat(currentText)
                }

                function updateResolutionsList() {
                    availableResolutionsList.clear()
                    const resolutions = preview.getAvailableResolutions()

                    for(let i = 0; i < resolutions.length; ++i) {
                        const txt = resolutions[i].toString()
                        availableResolutionsList.append({text: txt})
                    }               
                }
            }
        }

        CSlider { id: exposure; text: "Exposure"; from: 0; to: 10000; stepSize: 20; value: preview.cameraExposure; onMoved: preview.setCameraExposure(newValue) }
        CSlider { id: brightness; text: "Brightness"; from: -10; to: 10; stepSize: 1; value: preview.cameraBrightness; onMoved: preview.setCameraBrightness(newValue) }
        CSlider { id: contrast; text: "Contrast"; from: -10; to: 10; stepSize: 1; value: preview.cameraContrast; onMoved: preview.setCameraContrast(newValue) }
        CSlider { id: saturation; text: "Saturation"; from: 0; to: 100; stepSize: 1; value: preview.cameraSaturation; onMoved: preview.setCameraSaturation(newValue) }
        CSlider { id: wb; text: "White Balance"; from: 0; to: 10000; stepSize: 100; value: preview.cameraWhiteBalance; onMoved: preview.setCameraWhiteBalance(newValue) }
        CSlider { id: gamma; text: "Gamma"; from: 0; to: 1000; stepSize: 10; value: preview.cameraGamma; onMoved: preview.setCameraGamma(newValue) }
        CSlider { id: gain; text: "Gain"; from: 0; to: 100; stepSize: 1; value: preview.cameraGain; onMoved: preview.setCameraGain(newValue) }
        CSlider { id: sharpness; text: "Sharpness"; from: 0; to: 10; stepSize: 1; value: preview.cameraSharpness; onMoved: preview.setCameraSharpness(newValue) }

        CButton { 
            text: "Apply To All"
            enabled: preview.applyToAllBtnProperty
            opacity: enabled ? 1 : 0.3
            onClicked: { preview.setApplyToAllBtn() }
        }

        RowLayout {
            Layout.fillWidth: true

            CButton { text: "Choose destination folder"; onClicked: { root.dialog(); folderDialog.open() } }
            Label {
                text: folderDialog.currentFolder
            }

            FolderDialog {
                id: folderDialog
                folder: StandardPaths.standardLocations(StandardPaths.PicturesLocation)[0]
                
                Component.onCompleted: acquisition.changeSavingDirectory(folder)
                onAccepted: {
                    acquisition.changeSavingDirectory(folder)
                    root.dialog()
                    console.log("Accepted")
                }
                onRejected: {
                    root.dialog()
                    console.log("Rejected")
                }
            }
        }
    }
}