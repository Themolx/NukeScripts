# Nuke Grab Tool v2.0
#
# This script implements a "grab" tool similar to Blender's functionality.
# It allows users to move selected nodes by pressing 'E' and moving the mouse,
# without needing to click and drag directly on the nodes.
#
# Usage:
# 1. Select one or more nodes in Nuke
# 2. Press 'E' to activate the grab mode
# 3. Move the mouse to reposition the selected nodes
# 4. Left-click or press 'Enter' to confirm the new position
# 5. Press 'Esc' to cancel the operation







import nuke
from PySide2 import QtCore, QtGui, QtWidgets

class GrabTool(QtCore.QObject):
    def __init__(self):
        super(GrabTool, self).__init__()
        self.grab_active = False
        self.start_pos = None
        self.selected_nodes = []
        self.original_positions = {}
        self.scale_factor = 1.0
        self.original_cursor = None

    def activate_grab(self):
        self.selected_nodes = nuke.selectedNodes()
        if not self.selected_nodes:
            return  # Silent return if no nodes are selected
        
        self.grab_active = True
        self.original_positions = {node: (node.xpos(), node.ypos()) for node in self.selected_nodes}
        self.start_pos = QtGui.QCursor.pos()
        self.scale_factor = nuke.zoom()
        
        # Change cursor to a hand cursor
        app = QtWidgets.QApplication.instance()
        self.original_cursor = app.overrideCursor()
        app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        
        app.installEventFilter(self)

    def deactivate_grab(self):
        self.grab_active = False
        
        # Always restore the cursor
        app = QtWidgets.QApplication.instance()
        while app.overrideCursor() is not None:
            app.restoreOverrideCursor()
        
        if self.original_cursor:
            app.setOverrideCursor(self.original_cursor)
        
        QtWidgets.QApplication.instance().removeEventFilter(self)

    def apply_grab(self):
        self.deactivate_grab()

    def cancel_grab(self):
        for node, (x, y) in self.original_positions.items():
            node.setXYpos(x, y)
        self.deactivate_grab()

    def eventFilter(self, obj, event):
        if self.grab_active:
            if event.type() == QtCore.QEvent.MouseMove:
                # Change to closed hand cursor during movement
                app = QtWidgets.QApplication.instance()
                app.changeOverrideCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
                self.update_positions(event.globalPos())
            elif event.type() == QtCore.QEvent.MouseButtonRelease and event.button() == QtCore.Qt.LeftButton:
                self.apply_grab()  # Mouse release ends the grab
            elif event.type() == QtCore.QEvent.KeyPress:
                if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
                    self.apply_grab()
                elif event.key() == QtCore.Qt.Key_Escape:
                    self.cancel_grab()
        return False

    def update_positions(self, current_pos):
        offset = current_pos - self.start_pos
        scaled_offset = QtCore.QPoint(int(offset.x() / self.scale_factor), int(offset.y() / self.scale_factor))
        for node in self.selected_nodes:
            orig_x, orig_y = self.original_positions[node]
            node.setXYpos(orig_x + scaled_offset.x(), orig_y + scaled_offset.y())

grab_tool = GrabTool()

def grab_key_press():
    grab_tool.activate_grab()

# Add the Grab tool to Nuke's menu
nuke.menu('Nuke').addCommand('Edit/Grab Tool', grab_key_press, 'e')
