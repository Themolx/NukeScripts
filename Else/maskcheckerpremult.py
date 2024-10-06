import nuke

def mask_channel_splitter_with_individual_premults_and_hero_dot():
    try:
        node = nuke.selectedNode()
    except ValueError:
        nuke.message("Error: No node selected. Please select a node with mask channels and run the script again.")
        return

    all_channels = node.channels()
    mask_channels = [chan for chan in all_channels if chan.endswith('.mask')]
    if not mask_channels:
        nuke.message("No mask channels found in the selected node.")
        return

    offset_y = 250
    offset_x = 0
    all_created_nodes = []

    hero_dot = nuke.nodes.Dot(inputs=[node])
    hero_dot.setXYpos(node.xpos() + 34, node.ypos() + 200)
    hero_dot['label'].setValue("Beauty")
    hero_dot['note_font_size'].setValue(20)
    all_created_nodes.append(hero_dot)

    for channel in mask_channels:
        shuffle_node = nuke.nodes.Shuffle(
            name=f"{channel.split('.')[0]}_mask",
            inputs=[hero_dot],
            postage_stamp=True,
            hide_input=False
        )
        shuffle_node['in'].setValue(channel)
        shuffle_node['out'].setValue('alpha')
        all_created_nodes.append(shuffle_node)

        premult_node = nuke.nodes.Premult(
            name=f"Premult_{channel.split('.')[0]}",
            inputs=[shuffle_node, hero_dot]
        )
        all_created_nodes.append(premult_node)

        xpos = hero_dot.xpos() + offset_x
        ypos = hero_dot.ypos() + offset_y
        shuffle_node.setXYpos(xpos, ypos)
        premult_node.setXYpos(xpos, ypos + 100)

        offset_x += 200

    if all_created_nodes:
        bdX = min(node.xpos() for node in all_created_nodes) - 50
        bdY = min(node.ypos() for node in all_created_nodes) - 50
        bdW = max(node.xpos() + node.screenWidth() for node in all_created_nodes) - bdX + 100
        bdH = max(node.ypos() + node.screenHeight() for node in all_created_nodes) - bdY + 100

        backdrop = nuke.nodes.BackdropNode(
            xpos=bdX,
            bdwidth=bdW,
            ypos=bdY,
            bdheight=bdH,
            tile_color=0x7171C600,
            label='<center>MaskChecker'
        )
        backdrop['note_font_size'].setValue(42)
        backdrop['note_font'].setValue('Verdana')

    nuke.message(f"Created a hero Dot for beauty and {len(mask_channels)} individual Shuffle and Premult nodes for mask channels, wrapped in a MaskChecker backdrop positioned 100px lower.")

if __name__ == "__main__":
    mask_channel_splitter_with_individual_premults_and_hero_dot()
