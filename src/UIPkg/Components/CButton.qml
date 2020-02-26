import QtQuick 2.4
import QtQuick.Controls 2.0

Flow {
    id: container
    property alias text: button.text
    signal clicked()

    Button {
        id: button
        text: qsTr("My custom text")
        contentItem: CCenteredText {}

        onClicked: container.clicked()
    }
}
