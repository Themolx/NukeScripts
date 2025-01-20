#  Nuke Custom Tools 

## Overview

As a **Compositor** and **Technical Director**, I've developed tools to enhance workflow efficiency in **Nuke compositing**. This documentation outlines each tool's functionality.

---

## 📋 Table of Contents

1. [**Installation**](#installation)
2. [**Tools Overview**](#tools-overview)
   - [**General Tools**](#general-tools)
   - [**NodeGraph Tools**](#nodegraph-tools)
   - [**Shufflers**](#shufflers)
   - [**Loaders**](#loaders)
   - [**Miscellaneous**](#miscellaneous)
3. [**Conclusion**](#conclusion)

---

## 🚀 Installation

1. **Download** the tools package.
2. **Place** scripts in your **Nuke plugins directory**.
3. **Add** to your `init.py`:
   ```python
   nuke.pluginAddPath("/path/to/custom_tools")
   ```
4. **Restart** Nuke.

---

## 🛠️ Tools Overview

### 🔥 General Tools

#### **NukeGrabTool.py**

> **The hero script of this collection**. This advanced node movement tool mimics Nuke's native behavior while adding powerful features:
>
> - **Standard Grab (E)**: Moves only selected nodes.
>
> - **Input Tree Grab (Cmd+Option+E)**: Moves the selected node along with all its upstream nodes, ensuring proper context movement.
>
> - **Full Tree Grab (Cmd+E)**: Moves the entire node tree, both upstream and downstream, making it easy to reposition complex setups.
>
> - This tool significantly saves time and effort in managing node arrangements, especially for complex and interconnected node structures. 

#### **MergeCC.py**

> Merges color correction nodes, handling different types of color manipulations to streamline the merging process.

---

### 🖼️ NodeGraph Tools

#### **SmartBackdrop.py**

> Creates a backdrop for selected nodes, providing an organized layout with user-defined padding.

#### **NodeLabeler.py**

> Labels and colors animated nodes, providing visual cues for animated values. Changes are dynamically updated with callbacks.

#### **AdvancedShuffle.py**

> Manages node connections dynamically by shuffling and arranging them efficiently.

#### **DeleteAllBackdrops.py**

> Deletes all backdrop nodes in the current script, providing a quick cleanup option.

#### **CryptoMatteFixer.py**

> Fixes common issues in CryptoMatte nodes, ensuring proper matte extraction.

#### **CryptoLabeler.py**

> Labels CryptoMatte nodes automatically, simplifying workflows involving multiple matte passes.

---

### 🌟 Shufflers

#### **MaskCheckerPremult.py**

> Checks that masks are premultiplied correctly for consistency in downstream operations.

#### **BatchLightShuffler.py**

> Batch processes lighting layers, making it easier to manage complex setups.

#### **MaskCheckerGrade.py**

> Verifies mask grades for accuracy and consistency.

---

### 📦 Loaders

#### **CameraLoader.py**

> Loads camera data into Nuke, providing accurate camera movement for 3D integration.

#### **SequenceLoader.py**

> Loads sequences and creates Read nodes for streamlined loading.

#### **LoadLightningRender.py**

> Loads render layers, sets up Cryptomatte and premult nodes, and arranges nodes for easy setup.

#### **LoadLightningRenderFromRender.py**

> Loads lighting render layers, sets up Cryptomatte, Shuffle, and Premult nodes, and arranges them neatly.

#### **AppenderLoader.py**

> Loads sequences and creates AppendClip nodes for easy review with color-coded backdrops.

#### **OpenCompFromRender.py**

> Opens corresponding comp files based on selected Read nodes.

#### **NewShot Tools**

##### **NewCompShot.py**

> Sets up new comp shots by importing templates, loading renders, and updating settings.

##### **NewDenoiseComp.py**

> Assists with setting up denoise comp shots, ensuring proper setup.

---

### 🌀 Miscellaneous

#### **zdefocuschecker.py**

> Checks ZDefocus node settings for consistency.

#### **testik.py**

> A test script for experimental purposes.

---

## 🏁 Conclusion

These tools address common **VFX production challenges** with **time savings**, improved **consistency**, and enhanced **quality control**. I remain committed to expanding this toolkit based on feedback and evolving needs.

Feel free to reach out with questions or suggestions.

