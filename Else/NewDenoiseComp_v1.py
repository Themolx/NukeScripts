import nuke
import os
import re
from collections import Counter
from PySide2 import QtWidgets

def get_latest_comp_file():
    current_script = nuke.root().name()
    print(f"Current script path: {current_script}")

    match = re.search(r'(Z:/20105_Pysna_film/work/FILM/SQ\d+/SH\d+)/compositing_denoise/work/(.+)_denoise_v(\d+)\.nk', current_script)

    if not match:
        print("Error: Unable to parse the current script path.")
        return None

    base_path, file_prefix, _ = match.groups()
    comp_path = os.path.join(base_path, 'compositing', 'work')
    print(f"Searching for compositing files in: {comp_path}")

    if not os.path.exists(comp_path):
        print(f"Error: Directory does not exist: {comp_path}")
        return None

    all_files = [f for f in os.listdir(comp_path) if f.endswith('.nk')]
    comp_files = [f for f in all_files if re.search(r'SQ\d+_SH\d+_comp_v\d+\.nk', f)]

    if not comp_files:
        print("No compositing files found.")
        return None

    comp_files.sort(key=lambda x: int(re.search(r'v(\d+)', x).group(1)), reverse=True)
    latest_file = comp_files[0]
    print(f"Latest compositing file: {latest_file}")

    return os.path.join(comp_path, latest_file)

def import_latest_comp_file():
    latest_comp = get_latest_comp_file()

    if latest_comp:
        try:
            nuke.nodePaste(latest_comp)
            print(f"Successfully imported: {latest_comp}")
            nuke.message(f"Successfully imported: {os.path.basename(latest_comp)}")
            return True
        except Exception as e:
            error_message = f"Error importing file: {str(e)}"
            print(error_message)
            nuke.message(error_message)
    else:
        print("No compositing file to import.")
        nuke.message("No compositing file to import.")
    return False

def round_value(value):
    if isinstance(value, (int, float)):
        return round(value, 2)
    return value

def is_node_in_backdrop(node, backdrop):
    node_x, node_y = node.xpos(), node.ypos()
    bd_x, bd_y = backdrop.xpos(), backdrop.ypos()
    bd_r, bd_t = bd_x + backdrop['bdwidth'].value(), bd_y + backdrop['bdheight'].value()
    return bd_x <= node_x <= bd_r and bd_y <= node_y <= bd_t

def find_wrong_zdefocus_nodes():
    defocus_nodes = [n for n in nuke.allNodes() if 'PxF_ZDefocus' in n.name() and 'Controller' not in n.name()]
    
    if not defocus_nodes:
        nuke.message("No PxF_ZDefocusHERO nodes found in the script.")
        return
    
    print(f"Analyzing {len(defocus_nodes)} PxF_ZDefocusHERO nodes for wrong values:")
    
    purple_backdrops = [n for n in nuke.allNodes('BackdropNode') if n['tile_color'].value() == 2390460672]
    knobs_to_compare = ['fStop', 'focalDistance', 'focalLength', 'filmBack']
    
    wrong_nodes = {}
    correct_values = {}
    
    for knob in knobs_to_compare:
        knob_values = {}
        for node in defocus_nodes:
            if knob in node.knobs():
                value = round_value(node[knob].value())
                node_in_purple = any(is_node_in_backdrop(node, bd) for bd in purple_backdrops)
                if value not in knob_values:
                    knob_values[value] = []
                knob_values[value].append((node.name(), node_in_purple))
        
        if len(knob_values) > 1:
            most_common_value = Counter(round_value(node[knob].value()) for node in defocus_nodes if knob in node.knobs()).most_common(1)[0][0]
            correct_values[knob] = most_common_value
            
            for value, nodes in knob_values.items():
                if value != most_common_value:
                    if knob not in wrong_nodes:
                        wrong_nodes[knob] = []
                    wrong_nodes[knob].extend([(node, in_purple, value) for node, in_purple in nodes])
    
    if wrong_nodes:
        print("\nWrong nodes detected:")
        message = ["The following nodes have incorrect values:"]
        for knob, nodes in wrong_nodes.items():
            print(f"\n{knob} (Correct value: {correct_values[knob]}):")
            knob_message = [f"\n{knob} (Correct value: {correct_values[knob]}):"]
            for node, in_purple, value in nodes:
                print(f"  - {node}: {value}{' (in purple backdrop)' if in_purple else ''}")
                knob_message.append(f"  - {node}: {value}{' (in purple backdrop)' if in_purple else ''}")
            message.extend(knob_message)
        
        nuke.message("\n".join(message))
    else:
        print("\nNo wrong nodes found. All PxF_ZDefocusHERO nodes have consistent values.")
        nuke.message("No wrong nodes found. All PxF_ZDefocusHERO nodes have consistent values.")

def setup_2k_dcp_project():
    root = nuke.root()
    format_knob = root['format']
    
    desired_width, desired_height = 2048, 1080
    desired_pixel_aspect = 1.0
    desired_name = "2K_DCP"
    
    existing_format = None
    for format in nuke.formats():
        if (format.width() == desired_width and
            format.height() == desired_height and
            format.pixelAspect() == desired_pixel_aspect and
            format.name() == desired_name):
            existing_format = format
            break
    
    if existing_format:
        print(f"2K DCP format already exists. Setting project to use it.")
        format_knob.setValue(desired_name)
    else:
        print(f"2K DCP format not found. Creating and setting it.")
        new_format = f"{desired_width} {desired_height} {desired_pixel_aspect} {desired_name}"
        nuke.addFormat(new_format)
        format_knob.setValue(desired_name)
    
    root['lock_range'].setValue(True)
    
    current_format = format_knob.value()
    print(f"\nProject Format:")
    print(f"Name: {current_format.name()}")
    print(f"Resolution: {current_format.width()}x{current_format.height()}")
    print(f"Pixel Aspect Ratio: {current_format.pixelAspect()}")
    print(f"Lock Range: {root['lock_range'].value()}")

def set_viewer_process_rec709_aces():
    viewer_process = "Rec.709 (ACES)"
    viewers_updated = 0
    errors = []

    viewer_nodes = nuke.allNodes('Viewer')

    if not viewer_nodes:
        print("No Viewer nodes found. Creating a new Viewer node.")
        new_viewer = nuke.createNode('Viewer')
        viewer_nodes.append(new_viewer)

    for node in viewer_nodes:
        try:
            if 'viewerProcess' in node.knobs():
                node['viewerProcess'].setValue(viewer_process)
                viewers_updated += 1
            else:
                errors.append(f"Node {node.name()} does not have a viewerProcess knob.")
            
            if 'monitorOutOutputTransform' in node.knobs():
                node['monitorOutOutputTransform'].setValue(viewer_process)
            else:
                errors.append(f"Node {node.name()} does not have a monitorOutOutputTransform knob.")
        
        except Exception as e:
            errors.append(f"Error setting {viewer_process} for {node.name()}: {str(e)}")
    
    print(f"\nViewer Process Update Results:")
    print(f"Successfully updated {viewers_updated} Viewer node(s) to {viewer_process}")
    
    if errors:
        print("\nErrors encountered:")
        for error in errors:
            print(f"- {error}")
    else:
        print("No errors encountered.")

def comprehensive_setup():
    print("Starting comprehensive Nuke project setup...")
    setup_2k_dcp_project()
    set_viewer_process_rec709_aces()
    print("\nComprehensive setup complete!")

def create_white_alpha_node(input_node):
    remove_node = nuke.nodes.Remove(
        name='Remove1',
        channels='mask_extra',
        channels2='depth',
        channels3='mask',
        channels4='forward'
    )
    remove_node.setInput(0, input_node)
    remove_node.setXYpos(input_node.xpos(), input_node.ypos() + 50)
    
    shuffle_node = nuke.nodes.Shuffle(
        name='WHITE_ALPHA',
        label='WHITE_ALPHA',
        inputs=[remove_node],
        red='red',
        green='green',
        blue='blue',
        alpha='white'
    )
    shuffle_node.setXYpos(remove_node.xpos(), remove_node.ypos() + 50)
    
    return shuffle_node

def find_or_create_nodes():
    write_node = nuke.toNode('PFX_Write_MAIN')
    if not write_node:
        write_nodes = [n for n in nuke.allNodes() if n.Class() == "Write"]
        if write_nodes:
            write_node = write_nodes[0]
        else:
            nuke.message("No Write node found in the script.")
            return
    
    input_node = write_node.input(0)
    if not input_node:
        nuke.message("Write node has no input.")
        return
    
    if input_node.name() != 'WHITE_ALPHA':
        white_alpha_node = create_white_alpha_node(input_node)
        write_node.setInput(0, white_alpha_node)
        nuke.message("No white alpha and remove detected.. it is being added automatically")
        print("Created and connected Remove and WHITE_ALPHA nodes.")
    else:
        print("WHITE_ALPHA node already exists and is connected.")

def run_additional_checks():
    print("Running additional checks...")
    
    # Setup 2K DCP project
    comprehensive_setup()
    
    # Find mismatched ZDefocus nodes
    find_wrong_zdefocus_nodes()
    
    # Check for white alpha
    find_or_create_nodes()

def main():
    if import_latest_comp_file():
        run_additional_checks()
    else:
        print("Failed to import latest comp file. Additional checks not performed.")

# Run the main function
if __name__ == "__main__":
    main()