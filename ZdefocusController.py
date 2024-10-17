"""
ZDefocus Controller Script for Nuke - v16

This script creates or updates a centralized controller for all PxF_ZDefocusHERO nodes in a Nuke script.
It initializes the controller with camera values (except for focal plane) and sets all ZDefocus nodes to match the template.
The reset button updates camera values without changing the focal plane and without showing a dialog.

Last updated: 2023-10-02
"""

import nuke

def find_camera_hero():
    return next((n for n in nuke.allNodes() if n.Class() == "Camera2" and "CameraHERO" in n.name()), None)

def get_camera_values():
    camera_hero = find_camera_hero()
    if camera_hero:
        return {
            'focalLength': camera_hero['focal'].value() if 'focal' in camera_hero.knobs() else 32,
            'fstop': camera_hero['fstop'].value() if 'fstop' in camera_hero.knobs() else 5.6
        }
    return {'focalLength': 32, 'fstop': 5.6}  # Default values

def create_zdefocus_controller():
    global reset_controller_values  # Make this function globally accessible
    
    def reset_controller_values():
        controller = nuke.toNode('PxF_ZDefocusHERO_Controller')
        camera_values = get_camera_values()
        if controller:
            for knob, value in camera_values.items():
                if knob in controller.knobs():
                    controller[knob].setValue(value)
    
    existing_controller = nuke.toNode('PxF_ZDefocusHERO_Controller')
    if existing_controller:
        nuke.delete(existing_controller)

    zdefocus_nodes = [n for n in nuke.allNodes() if 'PxF_ZDefocus' in n.name()]
    for node in zdefocus_nodes:
        if not node.name().endswith('HERO'):
            node.setName(node.name() + 'HERO')

    if not zdefocus_nodes or not nuke.toNode('PFX_Write_MAIN'):
        nuke.message("Required nodes not found. Controller not created.")
        return

    camera_values = get_camera_values()
    controller = nuke.nodes.PostageStamp(name='PxF_ZDefocusHERO_Controller', note_font_size=40, hide_input=True)
    
    for knob_name, knob_label, knob_range in [
        ('disable_all', 'Disable All PxF_ZDefocusHERO', None),
        ('FocalPlane', 'Focal Plane', (0, 1000)),
        ('fstop', 'F-Stop', (0.1, 32)),
        ('focalLength', 'Focal Length', (15, 300))
    ]:
        knob = nuke.Boolean_Knob(knob_name, knob_label) if knob_name == 'disable_all' else nuke.Double_Knob(knob_name, knob_label)
        if knob_range:
            knob.setRange(*knob_range)
        controller.addKnob(knob)
        if knob_name in camera_values:
            knob.setValue(camera_values[knob_name])
        elif knob_name == 'disable_all':
            knob.setValue(False)
        elif knob_name == 'FocalPlane':
            knob.setValue(100)  # Default value for FocalPlane

    controller.addKnob(nuke.PyScript_Knob('reset', 'Reset to Camera Values', 'reset_controller_values()'))
    
    controller['knobChanged'].setValue("""
n = nuke.thisNode()
k = nuke.thisKnob()
if k.name() == "disable_all":
    n['tile_color'].setValue(int(0xffff00ff) if k.value() else int(0x00ff00ff))
    n['label'].setValue("Disabled" if k.value() else "Enabled")
""")
    controller['tile_color'].setValue(int(0x00ff00ff))
    controller['label'].setValue("Enabled")
    
    template_values = {
        'filter': 'bokeh',
        'useGPU': True,
        'resolution': '1:1',
        'controlChannel': 'depth.Z',
        'depthStyle': 'Real',
        'autofocus': (100, 100),
        'size': 15,
        'maxSize': 200,
        'aspect': 1,
        'mix': 1,
        'enableSim': True,
        'units': 'cm',
        'filmBack': 36,
        'viewKernel': False,
        'ringWidth': 0.25,
        'enableNoise': True,
        'noiseSize': 35,
        'noiseGain': 0.85,
        'noiseGamma': 0.85,
        'noiseMix': 0.33,
        'chromaAbEnable': True,
        'chromaAbScale': 1.02,
        'filterChannel': 'rgb colour'
    }
    
    for node in zdefocus_nodes:
        node['disable'].setExpression('[if {[python not nuke.executing()]} {return [value PxF_ZDefocusHERO_Controller.disable_all]} {return 0}]')
        
        for knob, value in template_values.items():
            if knob in node.knobs():
                node[knob].setValue(value)
        
        for knob, expression in [
            ('focalDistance', 'PxF_ZDefocusHERO_Controller.FocalPlane'),
            ('fStop', 'PxF_ZDefocusHERO_Controller.fstop'),
            ('focalLength', 'PxF_ZDefocusHERO_Controller.focalLength')
        ]:
            if knob in node.knobs():
                node[knob].setExpression(expression)
    
    write_node = nuke.toNode('PFX_Write_MAIN')
    controller.setXYpos(write_node.xpos() - 1000, write_node.ypos())
    
    backdrop = nuke.nodes.BackdropNode(label="Controller", note_font_size=42, tile_color=int(0xaaaaaaff), bdwidth=200, bdheight=200)
    backdrop.setXYpos(controller.xpos() - 50, controller.ypos() - 50)
    
    nuke.message(f"Created controller with camera values. {len(zdefocus_nodes)} ZDefocus nodes connected, renamed, and standardized with 'bokeh' filter.")

