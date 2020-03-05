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

            CSlider { id: totalAngle; labelSize: 180; text: "Total Angle (°)"; from: 0; to: 360; stepSize: 1; value: acquisition.totalAngle; onMoved: acquisition.setEngineTotalAngle(newValue) }
            CSlider { id: stepAngle; labelSize: 180; text: "Step Angle (°)"; from: 0; to: 90; stepSize: 1; value: acquisition.stepAngle; onMoved: acquisition.setEngineStepAngle(newValue) }
            CSlider { id: direction; labelSize: 180; text: "Direction (O = Left, 1 = Right)"; from: 0; to: 1; stepSize: 1; value: acquisition.direction; onMoved: acquisition.setEngineDirection(newValue)}
            CSlider { id: acceleration; labelSize: 180; text: "Acceleration (°)"; from: 0; to: 90; stepSize: 1; value: acquisition.acceleration; onMoved: acquisition.setEngineAcceleration(newValue) }
            CSlider { id: timeSpeed; labelSize: 180; text: "Time for 360° (s)"; from: 25; to: 90; stepSize: 1; value: acquisition.timeSpeed; onMoved: acquisition.setEngineTimeSpeed(newValue) }
            CheckBox {
                id: bsgi
                text: qsTr("BSGI")
                checked: acquisition.bsgi

                onToggled: {
                    acquisition.setEngineBSGI(checked)
                    bsgiAngle.enabled = !bsgiAngle.enabled
                }
            }
            CSlider { 
                id: bsgiAngle
                labelSize: 180
                text: "BSGI Angle (°)"
                from: 45
                to: 180
                stepSize: 45
                value: acquisition.bsgiAngle
                onMoved: acquisition.setEngineBSGIAngle(newValue)

                enabled : false
                opacity: enabled ? 1 : 0.3
            }
        }
    }
}