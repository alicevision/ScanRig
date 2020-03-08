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

                    for(let device in pythonList) {
                        const txt = "UVC: " + device.toString()
                        selectedDevices.append({name: txt}) //'name' is the key to access the attribute 'txt'
                    }                    
                }

                model: ListModel {
                    id: selectedDevices
                }
                
                delegate: Item {
                    height: 50
                    width: parent.width
                    Text {
                        text: name //'name' is the key to access the attribute
                    }
                }
            }
        }

        ColumnLayout {
            CCameraSettings { 
                id: cameraSettings
                Layout.fillWidth: true
                Layout.minimumWidth: 400
                Layout.maximumWidth: 400
                Layout.alignment: Qt.AlignTop

                onDialog: cameraPreview.changeTimer()
            }   

            ColumnLayout {
                // Layout.fillWidth: true
                // Layout.fillHeight: true

                CEngineConfiguration {
                    Layout.fillHeight: true
                    Layout.fillWidth: true
                    id: engineConfiguration
                }
            }     
        }
    }
}