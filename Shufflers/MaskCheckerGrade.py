set cut_paste_input [stack 0]
version 14.0 v5
push 0
push 0
push $cut_paste_input
Group {
 inputs 3
 name MolochMaskCreator
 tile_color 0x46c7c7ff
 note_font "Bitstream Vera Sans Bold"
 note_font_color 0xffffffff
 selected true
 xpos 1930
 ypos 283
 addUserKnob {20 Settings l "Screen Mattes"}
 addUserKnob {26 info l "" +STARTLINE T "This node copies alpha channels from inputs to dedicated matte channels.\nConnect screen mattes to inputs 1 and 2.\n\nOutputs:\n- matte_screen01.mask (from input 1)\n- matte_screen02.mask (from input 2)"}
 addUserKnob {26 ""}
 addUserKnob {26 credits l "" +STARTLINE T "Created by Martin Tomek"}
}
 Input {
  inputs 0
  name matte_screen02
  label matte_screen02
  xpos -119
  ypos 148
  number 2
 }
 Input {
  inputs 0
  name matte_screen01
  label matte_screen01
  xpos -133
  ypos 62
  number 1
 }
 Input {
  inputs 0
  name Input
  xpos 0
 }
add_layer {matte_screen01 matte_screen01.mask}
add_layer {matte_screen02 matte_screen02.mask}
 Copy {
  inputs 2
  from0 rgba.alpha
  to0 matte_screen01.mask
  name Copy1
  xpos 0
  ypos 86
  disable {{"[exists parent.input1] ? 0 : 1"}}
 }
 Copy {
  inputs 2
  from0 rgba.alpha
  to0 matte_screen02.mask
  name Copy2
  xpos 0
  ypos 153
  disable {{"[exists parent.input2] ? 0 : 1"}}
 }
 Output {
  name Output1
  xpos 0
  ypos 306
 }
 Viewer {
  frame 1041
  frame_range 986-1124
  fps 25
  viewerProcess "sRGB (ACES)"
  name Viewer1
  xpos 0
  ypos 232
 }
end_group
