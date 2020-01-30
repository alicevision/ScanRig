import QtQuick 2.4
import QtQuick.Controls 2.0

Flow {
    id: container
    property alias text: name.text
    signal clicked()

    Button {
        id: name
        text: qsTr("My custom text")
        onClicked: container.clicked()
    }
}
