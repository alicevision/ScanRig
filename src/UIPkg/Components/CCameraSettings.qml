import QtQuick 2.14
import QtQuick.Controls 2.14

Flow {
    Slider {
        from: 0
        value: backend.camExposure
        to: 4000
        onMoved: backend.setCamExposure(value)
    }

    Label {
        text: "Exposure"
    }
}
