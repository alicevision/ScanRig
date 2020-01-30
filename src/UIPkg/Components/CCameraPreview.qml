import QtQuick 2.14
import QtQuick.Layouts 1.14
import QtQuick.Controls 2.14

Flow {
    Image {
        id: camera
        property bool backBuffer: false

        source: "image://cameraProvider/0/" + backBuffer
        asynchronous: false
        fillMode: Image.PreserveAspectFit
        width: 200

        function reload() {
            backBuffer = !backBuffer
            source = "image://cameraProvider/0/" + backBuffer
        }

        Timer {
            interval: 16; running: true; repeat: true
            onTriggered: camera.reload()
        }
    }

    ComboBox {
        model: ["Camera 0", "Camera 1", "Camera 2"]
    }
}