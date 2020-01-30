import QtQuick 2.14
import QtQuick.Layouts 1.14
import QtQuick.Controls 2.14

GroupBox {
    title: "Camera Preview"
    
    Column {
        Image {
            id: camera
            property bool backBuffer: false
            property int camId: camList[0]

            source: "image://cameraProvider/" + camId + "/" + backBuffer
            asynchronous: false
            fillMode: Image.PreserveAspectFit
            width: 200

            function reload() {
                backBuffer = !backBuffer
                source = "image://cameraProvider/" + camId + "/" + backBuffer
            }

            Timer {
                interval: 16; running: true; repeat: true
                onTriggered: camera.reload()
            }
        }

        ComboBox {
            model: camList
            onActivated: camera.camId = camList[currentIndex]
        }
    }
}