import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14

GroupBox {
    title: qsTr("Camera Settings")

    ColumnLayout {
        anchors.fill: parent

        CSlider { id: exposure; text: "Exposure"; from: 0; to: 4000; stepSize: 1; value: preview.camExposure; onMoved: preview.setCamExposure(newValue) }
        CSlider { id: exposure2; text: "Exposure2"; from: 0; to: 2500; stepSize: 1; value: preview.camExposure; onMoved: preview.setCamExposure(newValue) }

    }
}