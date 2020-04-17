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
                id: photometricStereo
                text: qsTr("Photometric Stereo")
                checked: acquisition.photometricStereo

                onToggled: {
                    acquisition.setEnginePhotometricStereo(checked)
                    photometricStereoAngle.enabled = !photometricStereoAngle.enabled
                }
            }
            CSlider { 
                id: photometricStereoAngle
                labelSize: 180
                text: "Photometric Stereo Angle (°)"
                from: 45
                to: 180
                stepSize: 45
                value: acquisition.photometricStereoAngle
                onMoved: acquisition.setEnginePhotometricStereoAngle(newValue)

                enabled : false
                opacity: enabled ? 1 : 0.3
            }
        }
    }
}