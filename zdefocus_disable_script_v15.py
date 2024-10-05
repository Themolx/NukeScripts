import nuke
import nukescripts
from PySide2 import QtWidgets, QtCore, QtGui

class ZDefocusControllerWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ZDefocusControllerWidget, self).__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # Controls
        self.focal_plane = self.addSlider("Focal Plane", 0, 1000, 100)
        self.fstop = self.addSlider("F-Stop", 0.1, 32, 5.6)
        self.focal_length = self.addSlider("Focal Length", 15, 300, 50)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.link_button = QtWidgets.QPushButton("Link Nodes")
        self.link_button.clicked.connect(self.link_nodes)
        button_layout.addWidget(self.link_button)

        self.reset_button = QtWidgets.QPushButton("Reset to Camera")
        self.reset_button.clicked.connect(self.reset_to_camera)
        button_layout.addWidget(self.reset_button)

        layout.addLayout(button_layout)

        # Results area
        self.results_text = QtWidgets.QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        # Diagnostics button
        self.diag_button = QtWidgets.QPushButton("Run Diagnostics")
        self.diag_button.clicked.connect(self.run_diagnostics)
        layout.addWidget(self.diag_button)

    def addSlider(self, label, min_val, max_val, default_val):
        group = QtWidgets.QGroupBox(label)
        layout = QtWidgets.QHBoxLayout()
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(int(min_val * 10), int(max_val * 10))
        slider.setValue(int(default_val * 10))
        spin_box = QtWidgets.QDoubleSpinBox()
        spin_box.setRange(min_val, max_val)
        spin_box.setValue(default_val)
        spin_box.setSingleStep(0.1)
        
        slider.valueChanged.connect(lambda: spin_box.setValue(slider.value() / 10))
        slider.valueChanged.connect(lambda: self.update_nodes(label, slider.value() / 10))
        spin_box.valueChanged.connect(lambda: slider.setValue(int(spin_box.value() * 10)))
        spin_box.valueChanged.connect(lambda: self.update_nodes(label, spin_box.value()))
        
        layout.addWidget(slider)
        layout.addWidget(spin_box)
        group.setLayout(layout)
        self.layout().addWidget(group)
        return spin_box

    def update_nodes(self, label, value):
        for node in self.find_zdefocus_nodes():
            if label == "Focal Plane":
                node['focalDistance'].setValue(value)
            elif label == "F-Stop":
                node['fStop'].setValue(value)
            elif label == "Focal Length":
                node['focalLength'].setValue(value)

    def find_zdefocus_nodes(self):
        return [n for n in nuke.allNodes() if n.Class() == "PxF_ZDefocus"]

    def link_nodes(self):
        nodes = self.find_zdefocus_nodes()
        if not nodes:
            self.results_text.setText("No PxF_ZDefocus nodes found.")
            return
        
        for node in nodes:
            node['focalDistance'].setExpression(f"{self.focal_plane.value()}")
            node['fStop'].setExpression(f"{self.fstop.value()}")
            node['focalLength'].setExpression(f"{self.focal_length.value()}")
        
        self.results_text.setText(f"Linked {len(nodes)} PxF_ZDefocus nodes.")

    def reset_to_camera(self):
        camera = next((n for n in nuke.allNodes() if n.Class() == "Camera2" and "CameraHERO" in n.name()), None)
        if camera:
            self.focal_length.setValue(camera['focal'].value())
            self.fstop.setValue(camera['fstop'].value())
            self.results_text.setText("Reset values from CameraHERO.")
        else:
            self.results_text.setText("CameraHERO not found.")

    def run_diagnostics(self):
        nodes = self.find_zdefocus_nodes()
        if not nodes:
            self.results_text.setText("No PxF_ZDefocus nodes found.")
            return

        inconsistencies = []
        for knob in ['focalDistance', 'fStop', 'focalLength']:
            values = set(node[knob].value() for node in nodes)
            if len(values) > 1:
                inconsistencies.append(f"{knob}: {', '.join(map(str, values))}")

        if inconsistencies:
            self.results_text.setText("Inconsistencies found:\n" + "\n".join(inconsistencies))
        else:
            self.results_text.setText("All PxF_ZDefocus nodes have consistent values.")

class ZDefocusControllerPanel(nukescripts.PythonPanel):
    def __init__(self):
        nukescripts.PythonPanel.__init__(self, 'PxF_ZDefocus Controller', 'com.yourname.PxFZDefocusController')
        self.setMinimumSize(400, 500)
        
        # Create Qt widget and embed it in a knob
        self.custom_widget = ZDefocusControllerWidget()
        self.custom_knob = nuke.PyCustom_Knob("custom_knob", "", "")
        self.custom_knob.setCustom(self.custom_widget)
        self.addKnob(self.custom_knob)

    def showModalDialog(self):
        result = nukescripts.PythonPanel.showModalDialog(self)
        return result

def show_zdefocus_controller():
    global zdefocus_panel
    zdefocus_panel = ZDefocusControllerPanel()
    zdefocus_panel.show()

# Add menu item
nuke.menu('Pane').addCommand('PxF_ZDefocus Controller', show_zdefocus_controller)
nukescripts.registerPanel('com.yourname.PxFZDefocusController', show_zdefocus_controller)

# Run the script
show_zdefocus_controller()