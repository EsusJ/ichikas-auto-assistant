import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    property string labelText: ""
    property alias control: controlLoader.sourceComponent

    Label {
        text: labelText
        Layout.preferredWidth: 120
        Layout.alignment: Qt.AlignVCenter
    }

    Loader {
        id: controlLoader
        Layout.fillWidth: true
        Layout.alignment: Qt.AlignVCenter
    }
}