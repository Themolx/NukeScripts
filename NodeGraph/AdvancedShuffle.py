# DynamicShuffleLabeler.py v2.3

import nuke
import uuid

# User variable for vertical spacing (in pixels)
VERTICAL_SPACING = 10

# Unique identifier for nodes created by this script (hidden from user)
SCRIPT_ID = str(uuid.uuid4())

def is_keep_rgba_node(node):
    return (node.Class() == 'Remove' and 
            node['operation'].value() == 'keep' and 
            node['channels'].value() in ['rgba', 'rgb'])

def find_keep_rgba_node(shuffle_node):
    for dep in shuffle_node.dependent():
        if is_keep_rgba_node(dep) and dep.input(0) == shuffle_node:
            return dep
    return None

def create_keep_rgba_node(shuffle_node):
    try:
        remove_node = nuke.nodes.Remove()
        remove_node['operation'].setValue('keep')
        remove_node['channels'].setValue('rgba')
        remove_node['label'].setValue("keep rgba")
        remove_node.setInput(0, shuffle_node)
        
        # Only set position if the shuffle node has a valid position
        if shuffle_node.xpos() is not None and shuffle_node.ypos() is not None:
            remove_node.setXYpos(shuffle_node.xpos(), shuffle_node.ypos() + shuffle_node.screenHeight() + VERTICAL_SPACING)
        
        remove_node['script_id'] = nuke.String_Knob('script_id', 'Script ID', SCRIPT_ID)
        remove_node['script_id'].setFlag(nuke.INVISIBLE)
        
        return remove_node
    except Exception as e:
        print(f"Error creating Remove node: {str(e)}")
        return None

def get_shuffle_input(node):
    if node.Class() == 'Shuffle':
        return node['in'].value()
    elif node.Class() == 'Shuffle2':
        return node['in1'].value().split('.')[-1]
    return ''

def update_shuffle_node(node):
    if node.Class() in ['Shuffle', 'Shuffle2']:
        in_value = get_shuffle_input(node)
        
        if in_value.lower() != 'rgba':
            node['label'].setValue(f"[value {node.Class().lower()}.in]" if node.Class() == 'Shuffle' else '[value in1]')
            node['postage_stamp'].setValue(True)
            print(f"Updated {node.name()}: Label set to input channel, postage stamp turned on (in: {in_value})")
        else:
            node['label'].setValue('')
            node['postage_stamp'].setValue(False)
            print(f"Updated {node.name()}: Label cleared, postage stamp turned off (in: rgba)")

def on_user_create():
    node = nuke.thisNode()
    if node.Class() in ['Shuffle', 'Shuffle2']:
        update_shuffle_node(node)
        # Delay the creation of the Remove node
        nuke.executeInMainThread(lambda: create_remove_node_if_needed(node))

def create_remove_node_if_needed(node):
    if not find_keep_rgba_node(node):
        create_keep_rgba_node(node)

def on_knob_changed():
    node = nuke.thisNode()
    knob = nuke.thisKnob()
    
    if node.Class() in ['Shuffle', 'Shuffle2'] and knob and knob.name() in ['in', 'in1']:
        update_shuffle_node(node)

def setup_callbacks():
    nuke.removeOnUserCreate(on_user_create)
    nuke.removeKnobChanged(on_knob_changed)
    
    for node_class in ['Shuffle', 'Shuffle2']:
        nuke.addOnUserCreate(on_user_create, nodeClass=node_class)
        nuke.addKnobChanged(on_knob_changed, nodeClass=node_class)

def update_existing_shuffle_nodes():
    for node in nuke.allNodes():
        if node.Class() in ['Shuffle', 'Shuffle2']:
            update_shuffle_node(node)

def initialize_dynamic_shuffle_labeler():
    setup_callbacks()
    update_existing_shuffle_nodes()

# Run the initialization process when the script is loaded
initialize_dynamic_shuffle_labeler()

print(f"Dynamic Shuffle Labeler v2.3 initialized. Vertical spacing set to {VERTICAL_SPACING} pixels.")
