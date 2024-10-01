# MergeCC.py
import nuke
import math

def debug_print(message):
    print(f"DEBUG: {message}")

def multiply_values(a, b):
    debug_print(f"Multiplying: {a} * {b}")
    if isinstance(a, (float, int)) and isinstance(b, (float, int)):
        result = a * b
    elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        result = [a[i] * b[i] for i in range(min(len(a), len(b)))]
    elif isinstance(a, (list, tuple)) and isinstance(b, (float, int)):
        result = [v * b for v in a]
    elif isinstance(a, (float, int)) and isinstance(b, (list, tuple)):
        result = [a * v for v in b]
    else:
        raise TypeError("Unsupported types for multiplication")
    debug_print(f"Multiplication result: {result}")
    return result

def add_values(a, b):
    debug_print(f"Adding: {a} + {b}")
    if isinstance(a, (float, int)) and isinstance(b, (float, int)):
        result = a + b
    elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        result = [a[i] + b[i] for i in range(min(len(a), len(b)))]
    elif isinstance(a, (list, tuple)) and isinstance(b, (float, int)):
        result = [v + b for v in a]
    elif isinstance(a, (float, int)) and isinstance(b, (list, tuple)):
        result = [a + v for v in b]
    else:
        raise TypeError("Unsupported types for addition")
    debug_print(f"Addition result: {result}")
    return result

def combine_gamma_values(gamma_values):
    debug_print(f"Combining gamma values: {gamma_values}")
    log_sum = sum(math.log(g) for g in gamma_values)
    result = math.exp(log_sum)
    debug_print(f"Combined gamma result: {result}")
    return result

def merge_color_nodes():
    selected_nodes = nuke.selectedNodes()
    debug_print(f"Selected nodes: {[node.name() for node in selected_nodes]}")
    
    if not selected_nodes:
        nuke.message("No nodes selected.")
        return

    node_type = selected_nodes[0].Class()
    if not all(node.Class() == node_type for node in selected_nodes):
        nuke.message("Please select only ColorCorrect nodes or only Grade nodes, not a mix.")
        return

    if node_type == "ColorCorrect":
        merge_color_correct_nodes(selected_nodes)
    elif node_type == "Grade":
        merge_grade_nodes(selected_nodes)
    else:
        nuke.message("Please select either ColorCorrect or Grade nodes.")

def merge_color_correct_nodes(selected_nodes):
    debug_print("Merging ColorCorrect nodes")
    result = {}
    sections = ['master', 'shadows', 'midtones', 'highlights']
    attributes = ['saturation', 'contrast', 'gamma', 'gain', 'offset']

    for section in sections:
        for attr in attributes:
            key = f"{section}.{attr}" if section != 'master' else attr
            result[key] = 1.0 if attr != 'offset' else 0.0

    for node in selected_nodes:
        debug_print(f"Processing node: {node.name()}")
        for section in sections:
            for attr in attributes:
                key = f"{section}.{attr}" if section != 'master' else attr
                value = node[key].value()
                debug_print(f"  {key}: {value}")
                if attr in ['saturation', 'contrast', 'gain']:
                    result[key] = multiply_values(result[key], value)
                elif attr == 'offset':
                    result[key] = add_values(result[key], value)
                elif attr == 'gamma':
                    result[key] = combine_gamma_values([result[key], value])

    merged_node = nuke.nodes.ColorCorrect()
    debug_print("Created merged ColorCorrect node")
    
    for key, value in result.items():
        merged_node[key].setValue(value)
        debug_print(f"Set {key} to {value}")

    finalize_merged_node(merged_node, selected_nodes)

def merge_grade_nodes(selected_nodes):
    debug_print("Merging Grade nodes")
    result = {
        'channels': 'rgb',
        'blackpoint': 0, 'whitepoint': 1,
        'black': 0, 'white': 1,
        'multiply': 1, 'add': 0,
        'gamma': 1,
        'reverse': False,
        'black_clamp': True, 'white_clamp': True,
        'maskChannelMask': 'alpha',
        'maskChannelInput': 'none',
        'inject': False,
        'invert_mask': False,
        'fringe': False,
        'unpremult': 'none',
        'invert_unpremult': False,
        'mix_luminance': 0,
        'mix': 1
    }

    gamma_values = []

    for node in selected_nodes:
        debug_print(f"Processing node: {node.name()}")
        result['blackpoint'] = add_values(result['blackpoint'], node['blackpoint'].value())
        result['whitepoint'] = multiply_values(result['whitepoint'], node['whitepoint'].value())
        result['black'] = add_values(result['black'], node['black'].value())
        result['white'] = multiply_values(result['white'], node['white'].value())
        result['multiply'] = multiply_values(result['multiply'], node['multiply'].value())
        result['add'] = add_values(result['add'], node['add'].value())
        gamma_values.append(node['gamma'].value())
        result['reverse'] = result['reverse'] != node['reverse'].value()
        result['black_clamp'] = result['black_clamp'] and node['black_clamp'].value()
        result['white_clamp'] = result['white_clamp'] and node['white_clamp'].value()
        result['mix_luminance'] = add_values(result['mix_luminance'], node['mix_luminance'].value())
        result['mix'] = multiply_values(result['mix'], node['mix'].value())

        result['channels'] = node['channels'].value()
        result['maskChannelMask'] = node['maskChannelMask'].value()
        result['maskChannelInput'] = node['maskChannelInput'].value()
        result['inject'] = node['inject'].value()
        result['invert_mask'] = node['invert_mask'].value()
        result['fringe'] = node['fringe'].value()
        result['unpremult'] = node['unpremult'].value()
        result['invert_unpremult'] = node['invert_unpremult'].value()

    result['gamma'] = combine_gamma_values(gamma_values)

    merged_node = nuke.nodes.Grade()
    debug_print("Created merged Grade node")
    
    for key, value in result.items():
        merged_node[key].setValue(value)
        debug_print(f"Set {key} to {value}")

    finalize_merged_node(merged_node, selected_nodes)

def finalize_merged_node(merged_node, selected_nodes):
    # Find the topmost selected node
    topmost_node = min(selected_nodes, key=lambda n: n.ypos())
    
    # Set position for the merged node
    merged_node.setXYpos(topmost_node.xpos() + 100, topmost_node.ypos())
    
    # Set label and color
    merged_node['label'].setValue(f"Merged {merged_node.Class()}")
    blue_color = int('0x2166aaff', 16)
    merged_node['tile_color'].setValue(blue_color)
    
    # Find the appropriate input node
    input_node = find_appropriate_input(topmost_node)
    
    if input_node:
        # Connect the merged node to the appropriate input
        merged_node.setInput(0, input_node)
        
        # Connect all nodes that were connected to the selected nodes to the merged node
        for node in selected_nodes:
            for dependent in node.dependent():
                if dependent not in selected_nodes:
                    dependent.setInput(0, merged_node)
    
    debug_print(f"{merged_node.Class()} nodes merged successfully. New node created and connected.")

def find_appropriate_input(node):
    # Check inputs recursively
    def check_input(current_node, target_class):
        if not current_node:
            return None
        if current_node.Class() == target_class:
            return current_node
        return check_input(current_node.input(0), target_class)
    
    target_class = node.Class()
    input_node = node.input(0)
    
    while input_node:
        if input_node.Class() == target_class:
            # Found a node of the same type, keep looking upstream
            input_node = input_node.input(0)
        else:
            # Found a node of a different type, this is our target
            return input_node
    
    # If we've reached this point, there's no appropriate input found
    return None

def run_merge_color_nodes():
    debug_print("Starting merge_color_nodes function")
    merge_color_nodes()
    debug_print("Finished merge_color_nodes function")

# Add to Nuke's toolbar
toolbar = nuke.toolbar("Nodes")
m = toolbar.addMenu("Custom")
m.addCommand("MergeColorNodes", run_merge_color_nodes, icon="ColorMath.png", shortcut='Ctrl+Alt+R')