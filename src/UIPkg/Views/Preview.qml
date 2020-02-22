import QtQuick 2.0
import QtQuick.Layouts 1.14
import "../Components"

Item {
    RowLayout {
        anchors.fill: parent

        CCameraPreview { 
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignTop
        }

        CCameraSettings { 
            Layout.preferredWidth: parent.width*0.2
            Layout.minimumWidth: 400
            Layout.alignment: Qt.AlignTop
        } 
    }
}