import nuke
from collections import Counter

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

if __name__ == "__main__":
    find_wrong_zdefocus_nodes()
