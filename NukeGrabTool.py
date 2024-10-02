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
        self.locked = False  # Lock mechanism to prevent reactivation during operation
        self.lock_x = False  # Flag to lock movement to X-axis
        self.lock_y = False  # Flag to lock movement to Y-axis

    def activate_grab(self):
        if self.locked:  # Prevent new activation if currently active
            return
        
        self.selected_nodes = nuke.selectedNodes()
        if not self.selected_nodes:
            return  # Silent return if no nodes are selected

        self.grab_active = True
        self.locked = True  # Lock activation during grab
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
        self.locked = False  # Unlock after grab operation is completed
        self.lock_x = False  # Reset axis locks on deactivation
        self.lock_y = False
        
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
                # Intercept Z for locking the X-axis, and Y for locking the Y-axis
                if event.key() == QtCore.Qt.Key_Z:
                    self.lock_x = True  # Lock X-axis movement
                    self.lock_y = False  # Ensure Y-axis is unlocked
                    return True  # Consume the event, preventing further propagation
                elif event.key() == QtCore.Qt.Key_Y:
                    self.lock_y = True  # Lock Y-axis movement
                    self.lock_x = False  # Ensure X-axis is unlocked
                    return True  # Consume the event, preventing further propagation
                elif event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
                    self.apply_grab()
                    return True  # Consume the event
                elif event.key() == QtCore.Qt.Key_Escape:
                    self.cancel_grab()
                    return True  # Consume the event
        return False

    def update_positions(self, current_pos):
        offset = current_pos - self.start_pos
        scaled_offset = QtCore.QPoint(int(offset.x() / self.scale_factor), int(offset.y() / self.scale_factor))
        for node in self.selected_nodes:
            orig_x, orig_y = self.original_positions[node]
            # Move only in the X or Y direction based on the lock flags
            if self.lock_x:
                node.setXYpos(orig_x + scaled_offset.x(), orig_y)  # Lock Y-axis, move only on X-axis
            elif self.lock_y:
                node.setXYpos(orig_x, orig_y + scaled_offset.y())  # Lock X-axis, move only on Y-axis
            else:
                node.setXYpos(orig_x + scaled_offset.x(), orig_y + scaled_offset.y())  # Free movement

grab_tool = GrabTool()

def grab_key_press():
    grab_tool.activate_grab()

# Add the Grab tool to Nuke's menu
nuke.menu('Nuke').addCommand('Edit/Grab Tool', grab_key_press, 'e')
