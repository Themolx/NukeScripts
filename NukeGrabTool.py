# Nuke Advanced Grab Tool v5.1
#
# This script implements an advanced grab tool to mimic Nuke's native node movement behavior,
# with added auto-backdrop functionality that works in and out of grab mode.
#
# Features:
# - Standard Grab (E): Moves only selected nodes.
# - Input Tree Grab (Cmd+Option+E): Moves the selected node and all its upstream nodes.
# - Full Tree Grab (Cmd+E): Moves the entire connected node tree (upstream and downstream).
# - A-Tree Grab (Shift+A): Moves selected nodes and their entire A input trees.
# - Auto Backdrop (Shift+B): Creates a backdrop around affected/selected nodes.
# - Exit grab mode by pressing 'E' again
# - Option to keep nodes selected after exiting grab mode
# - Proper handling of zoom levels for consistent movement speed
# - Middle mouse button or Alt + Left click freezes movement without changing position on release

import nuke
from PySide2 import QtCore, QtGui, QtWidgets
import random
import colorsys

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

    def get_a_input_tree(self, node):
        tree = set([node])
        current = node.input(0)
        while current:
            tree.add(current)
            current = current.input(0)
        return tree

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
        elif self.grab_mode == "a_tree":
            self.affected_nodes = set()
            for node in self.selected_nodes:
                self.affected_nodes.update(self.get_a_input_tree(node))
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

    def create_auto_backdrop(self):
        nodes_to_backdrop = self.affected_nodes if self.grab_active else nuke.selectedNodes()
        if not nodes_to_backdrop:
            return

        # Calculate bounds
        bdX = min(node.xpos() for node in nodes_to_backdrop)
        bdY = min(node.ypos() for node in nodes_to_backdrop)
        bdW = max(node.xpos() + node.screenWidth() for node in nodes_to_backdrop) - bdX
        bdH = max(node.ypos() + node.screenHeight() for node in nodes_to_backdrop) - bdY

        # Expand the bounds
        left, top, right, bottom = (-80, -140, 80, 80)
        bdX += left
        bdY += top
        bdW += (right - left)
        bdH += (bottom - top)

        # Generate a light, unsaturated color
        hue = random.random()
        saturation = random.uniform(0.1, 0.3)
        value = random.uniform(0.7, 0.9)
        r, g, b = [int(255 * c) for c in colorsys.hsv_to_rgb(hue, saturation, value)]
        hex_color = int('%02x%02x%02x%02x' % (r, g, b, 255), 16)

        # Check for existing backdrops, groups, and interesting nodes
        existing_backdrops = [n for n in nodes_to_backdrop if n.Class() == 'BackdropNode']
        groups = [n for n in nodes_to_backdrop if n.Class() == 'Group']
        shuffles = [n for n in nodes_to_backdrop if n.Class() in ['Shuffle', 'Shuffle2']]

        # Find the node with the most inputs
        node_with_most_inputs = max(nodes_to_backdrop, key=lambda n: n.inputs())

        # Determine the backdrop name
        if groups:
            backdrop_name = f"{groups[0].name().rstrip('0123456789')}"
        elif shuffles:
            shuffle_values = set()
            for n in shuffles:
                if 'in1' in n.knobs():
                    shuffle_values.add(n['in1'].value())
            backdrop_name = ", ".join(sorted(shuffle_values))
        elif existing_backdrops:
            backdrop_name = f"{existing_backdrops[0].name().rstrip('0123456789')}_sub"
        else:
            backdrop_name = f"{node_with_most_inputs.Class()}_{node_with_most_inputs.name().rstrip('0123456789')}"

        # Create backdrop
        new_backdrop = nuke.nodes.BackdropNode(
            xpos=bdX,
            bdwidth=bdW,
            ypos=bdY,
            bdheight=bdH,
            tile_color=hex_color,
            note_font_size=42,
            name=backdrop_name
        )
        new_backdrop['label'].setValue(backdrop_name)

        # Set z-order
        if existing_backdrops:
            lowest_z_order = min(b['z_order'].value() for b in existing_backdrops)
            new_backdrop['z_order'].setValue(lowest_z_order - 1)
        else:
            new_backdrop['z_order'].setValue(0)

        # If in grab mode, apply the grab
        if self.grab_active:
            self.apply_grab()

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
                elif event.key() == QtCore.Qt.Key_B and event.modifiers() == QtCore.Qt.ShiftModifier:
                    self.create_auto_backdrop()
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

def grab_a_tree():
    grab_tool.activate_grab(mode="a_tree")

def create_auto_backdrop():
    grab_tool.create_auto_backdrop()

# Add the Grab tool commands to Nuke's menu
nuke.menu('Nuke').addCommand('Edit/Grab Tool', grab_standard, 'e')
nuke.menu('Nuke').addCommand('Edit/Grab Input Tree', grab_input_tree, 'ctrl+e')
nuke.menu('Nuke').addCommand('Edit/Grab Full Tree', grab_full_tree, 'alt+ctrl+e')
nuke.menu('Nuke').addCommand('Edit/Grab A-Tree', grab_a_tree, 'shift+a')
nuke.menu('Nuke').addCommand('Edit/Auto Backdrop', create_auto_backdrop, 'shift+b')
