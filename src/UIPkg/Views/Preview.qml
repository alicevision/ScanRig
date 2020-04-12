import QtQuick 2.0
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.14
import "../Components"

Item {
    RowLayout {
        anchors.fill: parent

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true

            CCameraPreview { 
                id: cameraPreview
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.alignment: Qt.AlignTop
                clip: true

                onChangedAcquisition: selectedDevicesList.refreshList()
                onChangedDevice: cameraSettings.res.updateResolutionsList()
            }

            ListView {
                id: selectedDevicesList

                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumHeight: 100

                function refreshList() {
                    selectedDevices.clear() //Clear the list
                    const pythonList = preview.getDevicesInAcquisition() //Get the devices inside the acquisition list

                    for(let device of pythonList) {
                        const txt = device.toString()
                        selectedDevices.append({name: txt}) //'name' is the key to access the attribute 'txt'
                    }                    
                }

                model: ListModel {
                    id: selectedDevices
                }

                Component.onCompleted: refreshList()
                
                delegate: Item {
                    height: 25
                    width: parent.width
                    
                    Rectangle {
                        anchors.fill: parent
                        color: palette.highlight
                        border.width: 2
                        border.color: palette.window
                    }
                    CCenteredText { text: name; font: font.family } //'name' is the key to access the attribute
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.minimumWidth: 400
            Layout.maximumWidth: 400

            CCameraSettings { 
                id: cameraSettings
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop

                onDialog: cameraPreview.changeTimer()
            }   

            ColumnLayout {
                CEngineConfiguration {
                    Layout.fillHeight: true
                    Layout.fillWidth: true
                    id: engineConfiguration
                }
            }     
        }
    }
}