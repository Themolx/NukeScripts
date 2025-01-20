# Nuke Advanced Grab Tool v3.8
#
# This script implements an advanced grab tool to mimic Nuke's native node movement behavior.
#
# Features:
# - Standard Grab (E): Moves only selected nodes.
# - Input Tree Grab (Cmd+Option+E): Moves the selected node and all its upstream nodes.
# - Full Tree Grab (Cmd+E): Moves the entire connected node tree (upstream and downstream).
# - Exit grab mode by pressing 'E' again
# - Option to keep nodes selected after exiting grab mode
# - Proper handling of zoom levels for consistent movement speed
# - Middle mouse button or Alt + Left click freezes movement without changing position on release
#
# Usage:
# 1. Select a node or nodes in Nuke
# 2. Press 'E' to move only the selected node(s)
# 3. Press 'Cmd+Option+E' to move the selected node and all its inputs
# 4. Press 'Cmd+E' to move the entire connected node tree
# 5. Move the mouse to reposition the nodes
# 6. Hold middle mouse button or Alt + Left click to freeze movement
# 7. Left-click, press 'Enter', or press 'E' again to confirm the new position
# 8. Press 'Esc' to cancel the operation
# 9. Press 'Z' to lock movement to X-axis, 'Y' to lock movement to Y-axis

import nuke
from PySide2 import QtCore, QtGui, QtWidgets

# User variable to control whether nodes remain selected after grab mode
KEEP_NODES_SELECTED = True

class AdvancedGrabTool(QtCore.QObject):
    def __init__(self):
        super(AdvancedGrabTool, self).__init__()
        self.grab_active = False
        self.start_pos = None
        self.last_pos = None
        self.selected_nodes = []
        self.affected_nodes = set()
        self.original_positions = {}
        self.current_positions = {}
        self.original_cursor = None
        self.locked = False
        self.lock_x = False
        self.lock_y = False
        self.grab_mode = "standard"
        self.freeze_movement = False
        self.alt_pressed = False

    def get_input_tree(self, node, upstream=None):
        if upstream is None:
            upstream = set()
        if node not in upstream:
            upstream.add(node)
            for i in range(node.inputs()):
                input_node = node.input(i)
                if input_node:
                    self.get_input_tree(input_node, upstream)
        return upstream

    def get_connected_nodes(self, start_node):
        connected = set()
        to_process = [start_node]
        
        while to_process:
            node = to_process.pop(0)
            if node not in connected:
                connected.add(node)
                
                inputs = node.dependencies(nuke.INPUTS | nuke.HIDDEN_INPUTS)
                to_process.extend([n for n in inputs if n not in connected])
                
                outputs = node.dependent(nuke.INPUTS | nuke.HIDDEN_INPUTS)
                to_process.extend([n for n in outputs if n not in connected])
        
        return connected

    def activate_grab(self, mode="standard"):
        if self.locked:
            return

        self.selected_nodes = nuke.selectedNodes()
        if not self.selected_nodes:
            return

        self.grab_active = True
        self.locked = True
        self.grab_mode = mode

        if self.grab_mode == "input_tree":
            self.affected_nodes = set()
            for node in self.selected_nodes:
                self.affected_nodes.update(self.get_input_tree(node))
        elif self.grab_mode == "full_tree":
            self.affected_nodes = set()
            for node in self.selected_nodes:
                self.affected_nodes.update(self.get_connected_nodes(node))
        else:  # standard mode
            self.affected_nodes = set(self.selected_nodes)

        self.original_positions = {node: (node.xpos(), node.ypos()) for node in self.affected_nodes}
        self.current_positions = self.original_positions.copy()

        self.start_pos = QtGui.QCursor.pos()
        self.last_pos = self.start_pos
        
        app = QtWidgets.QApplication.instance()
        self.original_cursor = app.overrideCursor()
        app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        
        app.installEventFilter(self)

        nuke.Undo().begin("Grab Tool")

    def deactivate_grab(self):
        self.grab_active = False
        self.locked = False
        self.lock_x = False
        self.lock_y = False
        self.grab_mode = "standard"
        self.freeze_movement = False
        self.last_pos = None
        self.alt_pressed = False
        
        app = QtWidgets.QApplication.instance()
        while app.overrideCursor() is not None:
            app.restoreOverrideCursor()

        if self.original_cursor:
            app.setOverrideCursor(self.original_cursor)
        
        QtWidgets.QApplication.instance().removeEventFilter(self)

        if not KEEP_NODES_SELECTED:
            for node in self.affected_nodes:
                node.setSelected(False)
        
        self.affected_nodes.clear()

        nuke.Undo().end()

    def apply_grab(self):
        for node, (x, y) in self.current_positions.items():
            node.setXYpos(int(x), int(y))
        self.deactivate_grab()

    def cancel_grab(self):
        for node, (x, y) in self.original_positions.items():
            node.setXYpos(x, y)
        self.deactivate_grab()

    def eventFilter(self, obj, event):
        if self.grab_active:
            if event.type() == QtCore.QEvent.MouseMove:
                app = QtWidgets.QApplication.instance()
                app.changeOverrideCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
                if not self.freeze_movement:
                    self.update_positions(event.globalPos())
            elif event.type() == QtCore.QEvent.MouseButtonPress:
                if event.button() == QtCore.Qt.MiddleButton:
                    self.freeze_movement = True
                elif event.button() == QtCore.Qt.LeftButton and self.alt_pressed:
                    self.freeze_movement = True
            elif event.type() == QtCore.QEvent.MouseButtonRelease:
                if event.button() == QtCore.Qt.LeftButton and not self.alt_pressed:
                    self.apply_grab()
                elif event.button() == QtCore.Qt.MiddleButton or (event.button() == QtCore.Qt.LeftButton and self.alt_pressed):
                    self.freeze_movement = False
                    self.last_pos = event.globalPos()
            elif event.type() == QtCore.QEvent.KeyPress:
                if event.key() == QtCore.Qt.Key_Alt:
                    self.alt_pressed = True
                elif event.key() == QtCore.Qt.Key_Z:
                    self.lock_x = True
                    self.lock_y = False
                    return True
                elif event.key() == QtCore.Qt.Key_Y:
                    self.lock_y = True
                    self.lock_x = False
                    return True
                elif event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
                    self.apply_grab()
                    return True
                elif event.key() == QtCore.Qt.Key_Escape:
                    self.cancel_grab()
                    return True
                elif event.key() == QtCore.Qt.Key_E:
                    self.apply_grab()
                    return True
            elif event.type() == QtCore.QEvent.KeyRelease:
                if event.key() == QtCore.Qt.Key_Alt:
                    self.alt_pressed = False
                    if self.freeze_movement:
                        self.freeze_movement = False
                        self.last_pos = QtGui.QCursor.pos()
        return False

    def update_positions(self, current_pos):
        if self.last_pos is None:
            self.last_pos = self.start_pos

        offset = current_pos - self.last_pos
        
        # Get the current zoom level
        zoom = nuke.zoom()
        
        # Apply zoom-adjusted scaling
        scaled_offset = QtCore.QPointF(offset.x() / zoom, offset.y() / zoom)
        
        for node in self.affected_nodes:
            current_x, current_y = self.current_positions[node]
            if self.lock_x:
                new_x = current_x + scaled_offset.x()
                new_y = current_y
            elif self.lock_y:
                new_x = current_x
                new_y = current_y + scaled_offset.y()
            else:
                new_x = current_x + scaled_offset.x()
                new_y = current_y + scaled_offset.y()
            
            self.current_positions[node] = (new_x, new_y)
            node.setXYpos(int(new_x), int(new_y))

        self.last_pos = current_pos

grab_tool = AdvancedGrabTool()

def grab_standard():
    if grab_tool.grab_active:
        grab_tool.apply_grab()
    else:
        grab_tool.activate_grab(mode="standard")

def grab_input_tree():
    grab_tool.activate_grab(mode="input_tree")

def grab_full_tree():
    grab_tool.activate_grab(mode="full_tree")

# Add the Grab tool commands to Nuke's menu
nuke.menu('Nuke').addCommand('Edit/Grab Tool', grab_standard, 'e')
nuke.menu('Nuke').addCommand('Edit/Grab Input Tree', grab_input_tree, 'ctrl+e')
nuke.menu('Nuke').addCommand('Edit/Grab Full Tree', grab_full_tree, 'alt+ctrl+e')
