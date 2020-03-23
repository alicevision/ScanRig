import QtQuick 2.14
import QtQuick.Controls 2.14
import QtQuick.Layouts 1.14

Item {
    id: container
    property alias text: name.text
    property alias from: slider.from
    property alias to: slider.to
    property alias value: slider.value
    property alias stepSize: slider.stepSize
    signal moved(int newValue)

    property int labelSize: 90
    height: 20
    
    RowLayout {
        anchors.fill: parent
        spacing: 10

        Label {
            id: name
            Layout.preferredWidth: container.labelSize
            text: ""
            horizontalAlignment: Text.AlignRight
        }

        Slider {
            id: slider
            from: 0
            value: 0
            to: 4000
            stepSize: 1
            onMoved : container.moved(value)
        }

        Label {
            id: result
            text: slider.value
            horizontalAlignment: Text.AlignLeft
        }
    }
}