# Nuke Advanced Grab Tool v3.2
#
# This script implements an advanced grab tool to mimic Nuke's native node movement behavior.
#
# Features:
# - Standard Grab (E): Moves only selected nodes.
# - Input Tree Grab (Cmd+Option+E): Moves the selected node and all its upstream nodes.
# - Full Tree Grab (Cmd+E): Moves the entire connected node tree (upstream and downstream).
# - Exit grab mode by pressing 'E' again
# - Option to keep nodes selected after exiting grab mode (controlled by user variable)
#
# Usage:
# 1. Select a node or nodes in Nuke
# 2. Press 'E' to move only the selected node(s)
# 3. Press 'Cmd+Option+E' to move the selected node and all its inputs
# 4. Press 'Cmd+E' to move the entire connected node tree
# 5. Move the mouse to reposition the nodes
# 6. Left-click, press 'Enter', or press 'E' again to confirm the new position
# 7. Press 'Esc' to cancel the operation
# 8. Press 'Z' to lock movement to X-axis, 'Y' to lock movement to Y-axis

import nuke
from PySide2 import QtCore, QtGui, QtWidgets

# User variable to control whether nodes remain selected after grab mode
# Note: Disabling this may be better for non-commercial versions of Nuke
KEEP_NODES_SELECTED = True

class AdvancedGrabTool(QtCore.QObject):
    def __init__(self):
        super(AdvancedGrabTool, self).__init__()
        self.grab_active = False
        self.start_pos = None
        self.selected_nodes = []
        self.affected_nodes = set()
        self.original_positions = {}
        self.scale_factor = 1.0
        self.original_cursor = None
        self.locked = False
        self.lock_x = False
        self.lock_y = False
        self.grab_mode = "standard"

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
                
                # Add all inputs (dependencies)
                inputs = node.dependencies(nuke.INPUTS | nuke.HIDDEN_INPUTS)
                to_process.extend([n for n in inputs if n not in connected])
                
                # Add all outputs (dependents)
                outputs = node.dependent(nuke.INPUTS | nuke.HIDDEN_INPUTS)
                to_process.extend([n for n in outputs if n not in connected])
        
        return connected

    def activate_grab(self, mode="standard"):
        if self.locked:
            return

        self.selected_nodes = nuke.selectedNodes()
        if not self.selected_nodes:
            #nuke.message("Please select a node before activating the grab tool.")
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

        self.start_pos = QtGui.QCursor.pos()
        self.scale_factor = nuke.zoom()
        
        app = QtWidgets.QApplication.instance()
        self.original_cursor = app.overrideCursor()
        app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        
        app.installEventFilter(self)

    def deactivate_grab(self):
        self.grab_active = False
        self.locked = False
        self.lock_x = False
        self.lock_y = False
        self.grab_mode = "standard"
        
        app = QtWidgets.QApplication.instance()
        while app.overrideCursor() is not None:
            app.restoreOverrideCursor()

        if self.original_cursor:
            app.setOverrideCursor(self.original_cursor)
        
        QtWidgets.QApplication.instance().removeEventFilter(self)

        # Keep nodes selected if the user variable is set to True
        if not KEEP_NODES_SELECTED:
            for node in self.affected_nodes:
                node.setSelected(False)
        
        self.affected_nodes.clear()

    def apply_grab(self):
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
                self.update_positions(event.globalPos())
            elif event.type() == QtCore.QEvent.MouseButtonRelease and event.button() == QtCore.Qt.LeftButton:
                self.apply_grab()
            elif event.type() == QtCore.QEvent.KeyPress:
                if event.key() == QtCore.Qt.Key_Z:
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
        return False

    def update_positions(self, current_pos):
        offset = current_pos - self.start_pos
        scaled_offset = QtCore.QPoint(int(offset.x() / self.scale_factor), int(offset.y() / self.scale_factor))
        
        for node in self.affected_nodes:
            orig_x, orig_y = self.original_positions[node]
            if self.lock_x:
                node.setXYpos(orig_x + scaled_offset.x(), orig_y)
            elif self.lock_y:
                node.setXYpos(orig_x, orig_y + scaled_offset.y())
            else:
                node.setXYpos(orig_x + scaled_offset.x(), orig_y + scaled_offset.y())

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
