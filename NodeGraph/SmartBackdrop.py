import nuke
import random
import colorsys
import re

class AutoBackdropPlus:
    def __init__(self):
        self.grab_active = False
        self.affected_nodes = []
        self.original_positions = {}
        self.character_list = [
            "matte_Ball.mask", "matte_Bijou.mask", "matte_Bird.mask", "matte_Butterfly.mask",
            "matte_Ceremonial.mask", "matte_Coalman.mask", "matte_counselorMaximus.mask",
            "matte_CounselorTycka.mask", "matte_CourtiemanA.mask", "matte_CourtiemanB.mask",
            "matte_CourtiemanC.mask", "matte_CourtiemanD.mask", "matte_CourtiewomanA.mask",
            "matte_CourtiewomanB.mask", "matte_CourtiewomanC.mask", "matte_CourtiewomanD.mask",
            "matte_Fish.mask", "matte_Flower.mask", "matte_Horse.mask", "matte_Hugo.mask",
            "matte_Jakub.mask", "matte_KingMiroslav.mask", "matte_Ladybug.mask", "matte_Maidservant.mask",
            "matte_Miller.mask", "matte_MusicianA.mask", "matte_MusicianB.mask", "matte_MusicianC.mask",
            "matte_Nanny.mask", "matte_OldKing.mask", "matte_PeasantA.mask", "matte_PeasantB.mask",
            "matte_PeasantJanek.mask", "matte_Prince.mask", "matte_PrincessKrasomila.mask",
            "matte_Raven.mask", "matte_ServantPrinceA.mask", "matte_ServantPrinceB.mask",
            "matte_ServantA.mask", "matte_ServantB.mask", "matte_Shoemaker.mask", "matte_SoldierA.mask",
            "matte_SoldierB.mask", "matte_SoldierC.mask", "matte_SoldierD.mask", "matte_SoldierE.mask",
            "matte_SoldierF.mask", "matte_SoldierG.mask", "matte_SoldierH.mask", "matte_SoldierI.mask",
            "matte_SoldierJ.mask", "matte_TaxCollector.mask", "matte_Weasel.mask"
        ]

    def create_copy_node(self):
        copy_node = nuke.nodes.Copy(
            inputs=[nuke.selectedNode(), nuke.nodes.Input()],
            from0="rgba.alpha",
            to0="matte_Bijou.mask",
            bbox="B",
            name="Copy_Mask_From_Crypto"
        )
        
        # Add custom knobs
        tab = nuke.Tab_Knob('Mask_Layers', 'Mask Layers')
        copy_node.addKnob(tab)
        
        matte_char_knob = nuke.Enumeration_Knob('Matte_char', '', self.character_list)
        copy_node.addKnob(matte_char_knob)
        
        get_crypto_btn = nuke.PyScript_Knob('get_from_crypto', 'Get layer from Cryptomatte', self.get_from_crypto_script())
        copy_node.addKnob(get_crypto_btn)
        
        set_channel_btn = nuke.PyScript_Knob('set_channel_button', 'Set channel to target knob', self.set_channel_script())
        copy_node.addKnob(set_channel_btn)
        
        settings_tab = nuke.Tab_Knob('settings_group', 'settings')
        copy_node.addKnob(settings_tab)
        
        autoset_knob = nuke.Boolean_Knob('autoset', 'Autoset channels after getting layer from Cryptomatte')
        autoset_knob.setValue(True)
        copy_node.addKnob(autoset_knob)
        
        force_wildcard_knob = nuke.Boolean_Knob('force_wildcard_enabled', 'Force character wildcard to refresh cryptomatte selection')
        force_wildcard_knob.setValue(True)
        copy_node.addKnob(force_wildcard_knob)
        
        knob_target = nuke.String_Knob('knob_target', 'Output channel knob target name')
        knob_target.setValue('to0')
        copy_node.addKnob(knob_target)
        
        version_text = nuke.Text_Knob('text', '', '\nVersion 0.6')
        copy_node.addKnob(version_text)
        
        end_group = nuke.EndTabGroup_Knob('endGroup')
        copy_node.addKnob(end_group)
        
        return copy_node

    def get_from_crypto_script(self):
        return '''
def read_cryptomatte_list(cryptomatte_node):
    if cryptomatte_node and cryptomatte_node.Class() == 'Cryptomatte':
        matte_list = cryptomatte_node['matteList'].value()
        return matte_list
    else:
        return None

def set_character_matte_list(copy_node=nuke.thisNode()):
    matte_char_knob = copy_node['Matte_char']
    character_list = list(enumerate(matte_char_knob.values()))
    node_input_a = copy_node.input(1)
    if not node_input_a:
        nuke.message('Please connect A input to Cryptomatte node')
        return
    
    cryptomatte_node = None
    if 'Cryptomatte' in node_input_a.Class():
        cryptomatte_node = node_input_a
    else:
        input_node = node_input_a.input(0)
        for _ in range(20):
            if not input_node:
                break
            input_node_class = input_node.Class()
            if 'Cryptomatte' in input_node_class:
                cryptomatte_node = input_node
                break
            else:
                input_node = input_node.input(0)

    if not cryptomatte_node:
        nuke.message('No Cryptomatte node found')
        return

    cryptomatte_list_str = read_cryptomatte_list(cryptomatte_node)
    autoset_knob = copy_node['autoset']
    force_wildcard_enabled = copy_node['force_wildcard_enabled'].value()

    if not cryptomatte_list_str:
        nuke.message('Please connect A input to Cryptomatte node with valid Matte list')
        return

    char_name = ''
    wildcard = ''
    for char_channel in sorted(character_list, key=lambda x: len(x[1]), reverse=True):
        if char_channel[1]:
            char_channel_name = re.search(r'matte_(\\w+)\\.mask', char_channel[1])
            if char_channel_name:
                char_name = char_channel_name.group(1)
                for special_case in ('Soldier', 'Peasant', 'Servant', 'Courtieman', 'Courtiewoman'):
                    if special_case in char_name:
                        matching_pattern = r'({case}[a-z]+{letter})'.format(
                            case=special_case, letter=char_name[-1])
                        break
                else:
                    matching_pattern = r'({})'.format(char_name)
                
                search_result = re.search(matching_pattern, cryptomatte_list_str, re.IGNORECASE)
                if search_result:
                    matched_name = search_result.group(1)
                    wildcard = matched_name + '*'
                    matte_char_knob.setValue(char_channel[0])
                    if autoset_knob.value():
                        copy_node['set_channel_button'].execute()
                    break
    
    if not wildcard:
        nuke.message('Did not find any match in Cryptomatte node Matte list')
    if force_wildcard_enabled and cryptomatte_list_str and wildcard:
        push_char_wildcard_to_cryptomatte(wildcard, cryptomatte_node)

set_character_matte_list()
'''

    def set_channel_script(self):
        return '''
def set_channel(this_copy_node=nuke.thisNode()):
    matte_char_knob = this_copy_node['Matte_char']
    matte_char_channel_name = matte_char_knob.value()
    knob_target_selection = this_copy_node['knob_target'].value()
    
    if not knob_target_selection:
        nuke.message('No target knob selected')
        return
    
    dest_channel_knob = this_copy_node.knob(knob_target_selection)
    if dest_channel_knob:
        if matte_char_channel_name not in nuke.channels():
            channel_name = matte_char_channel_name.split('.')[0]
            print('Channel not found, creating channel {}'.format(channel_name))
            nuke.Layer(channel_name, [matte_char_channel_name])
        dest_channel_knob.setValue(matte_char_channel_name)
    else:
        nuke.message('{} channel target knob not found'.format(knob_target_selection))

set_channel()
'''

    def get_backdrop_name(self, nodes):
        # Prioritize "to" values from Copy nodes
        for node in nodes:
            if node.Class() == 'Copy':
                for i in range(4):
                    knob_name = f'to{i}'
                    if knob_name in node.knobs():
                        channel_value = node[knob_name].value()
                        if channel_value:
                            return channel_value.split('.')[0]
        
        # Check for Merge nodes
        merge_nodes = [n for n in nodes if n.Class() == 'Merge2']
        if merge_nodes:
            operations = set(n['operation'].value() for n in merge_nodes)
            if len(operations) == 1:
                return operations.pop()
            return "Merge"
        
        # Rest of the backdrop naming logic remains the same
        # ... [previous backdrop naming logic]

    def create_auto_backdrop(self):
        # ... [previous create_auto_backdrop implementation]

    def toggle_grab(self):
        # ... [previous toggle_grab implementation]

    def apply_grab(self):
        # ... [previous apply_grab implementation]

# Create menu items
toolbar = nuke.menu('Nodes')
user_tools = toolbar.addMenu('AutoBackdropPlus', icon='BackdropNode.png')

# Create instance of the class
backdrop_tool = AutoBackdropPlus()

# Add menu items
user_tools.addCommand('Create Backdrop', lambda: backdrop_tool.create_auto_backdrop(), 'alt+b')
user_tools.addCommand('Toggle Grab', lambda: backdrop_tool.toggle_grab(), 'shift+g')
user_tools.addCommand('Create Character Copy', lambda: backdrop_tool.create_copy_node(), 'shift+c')
