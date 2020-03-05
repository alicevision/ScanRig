import QtQuick 2.14
import QtQuick.Layouts 1.14
import QtQuick.Controls 2.14

GroupBox {
    title: qsTr("Engine Configuration")

    ColumnLayout {
        CButton { 
            enabled: true
            opacity: enabled ? 1 : 0.3

            text: qsTr("Start Engine") 
            onClicked: {
                acquisition.startEngine()
                enabled = false
                configurationSettings.enabled = true
            }
        }

        ColumnLayout {
            spacing: 10
            id: configurationSettings

            enabled: false
            opacity: enabled ? 1 : 0.3

            CSlider { id: totalAngle; labelSize: 180; text: "Total Angle (°)"; from: 0; to: 360; stepSize: 1; value: 180 }
            CSlider { id: stepAngle; labelSize: 180; text: "Step Angle (°)"; from: 0; to: 90; stepSize: 1; value: 15 }
            CSlider { id: direction; labelSize: 180; text: "Direction (O = Left, 1 = Right)"; from: 0; to: 1; stepSize: 1; value: 0 }
            CSlider { id: acceleration; labelSize: 180; text: "Acceleration (°)"; from: 0; to: 90; stepSize: 1; value: 45 }
            CSlider { id: timeSpeed; labelSize: 180; text: "Time for 360° (s)"; from: 25; to: 90; stepSize: 1; value: 50 }
            CheckBox {
                text: qsTr("BSGI")
                checked: false
            }
        }
    }
}