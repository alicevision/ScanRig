import QtQuick 2.4
import QtQuick.Controls 2.0

Rectangle {
    id: container
    property alias text: name.text
    signal clicked()

    width: 50
    height: 50
    color: "#ffffff"

    Button {
        id: name
        text: qsTr("My custom text")
        onClicked: container.clicked()
    }
}
