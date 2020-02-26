import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14
import Qt.labs.platform 1.1

GroupBox {
    title: qsTr("Camera Settings")

    ColumnLayout {
        spacing: 10

        CSlider { id: exposure; text: "Exposure"; from: 0; to: 10000; stepSize: 20; value: preview.camExposure; onMoved: preview.setCamExposure(newValue) }
        CSlider { id: brightness; text: "Brightness"; from: -10; to: 10; stepSize: 1; value: preview.camBrightness; onMoved: preview.setCamBrightness(newValue) }
        CSlider { id: contrast; text: "Contrast"; from: -10; to: 10; stepSize: 1; value: preview.camContrast; onMoved: preview.setCamContrast(newValue) }
        CSlider { id: saturation; text: "Saturation"; from: 0; to: 100; stepSize: 1; value: preview.camSaturation; onMoved: preview.setCamSaturation(newValue) }
        CSlider { id: wb; text: "White Balance"; from: 0; to: 10000; stepSize: 100; value: preview.camWhiteBalance; onMoved: preview.setCamWhiteBalance(newValue) }
        CSlider { id: gamma; text: "Gamma"; from: 0; to: 1000; stepSize: 10; value: preview.camGamma; onMoved: preview.setCamGamma(newValue) }
        CSlider { id: gain; text: "Gain"; from: 0; to: 100; stepSize: 1; value: preview.camGain; onMoved: preview.setCamGain(newValue) }
        CSlider { id: sharpness; text: "Sharpness"; from: 0; to: 10; stepSize: 1; value: preview.camSharpness; onMoved: preview.setCamSharpness(newValue) }

        RowLayout {
            Layout.fillWidth: true

            CButton { text: "Choose destination folder"; onClicked: folderDialog.open() }
            Label {
                text: folderDialog.currentFolder
            }

            FolderDialog {
                id: folderDialog
                folder: StandardPaths.standardLocations(StandardPaths.PicturesLocation)[0]
                
                Component.onCompleted: acquisition.changeSavingDirectory(folder)
                onAccepted: acquisition.changeSavingDirectory(folder)
            }
        }
    }
}