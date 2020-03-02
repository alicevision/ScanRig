import QtQuick 2.0
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.14
import "../Components"

Item {
    ColumnLayout {
        anchors.fill: parent

        CButton { 
            enabled: true
            opacity: enabled ? 1 : 0.3

            text: qsTr("Start Engine") 
            onClicked: {
                acquisition.startEngine()
                enabled = false
                engineConfiguration.enabled = true
            }
        }

        CEngineConfiguration {
            Layout.fillHeight: true
            Layout.fillWidth: true
            id: engineConfiguration
            enabled: false
            opacity: enabled ? 1 : 0.3
        }
    }
}
