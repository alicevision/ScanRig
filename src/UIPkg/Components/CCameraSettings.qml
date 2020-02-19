import QtQuick 2.14
import QtQuick.Controls 2.14

GroupBox {
    title: "Camera Settings"

    Flow {
        Slider {
            id: expo
            from: 0
            value: preview.camExposure
            to: 4000
            stepSize: 1
            onMoved: preview.setCamExposure(value)

            Label {
                text: parent.value
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }

        Label {
            text: "Exposure"
        }
    }
}
