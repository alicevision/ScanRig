import QtQuick 2.4
import QtQuick.Controls 2.0

Text {
    id: content

    anchors.fill: parent
    verticalAlignment: Text.AlignVCenter
    horizontalAlignment: Text.AlignHCenter
    text: parent.text
    font: parent.font
    color: "#C8C8C8"
}
