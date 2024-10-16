# Nuke Custom Tools

---

## Overview

As a **Compositor** and **Technical Director**, I've developed various tools to enhance workflow efficiency and solve common problems in **Nuke compositing pipelines**. This documentation outlines the functionality and benefits of each tool.

---

## Table of Contents

1. [**Installation**](#installation)
2. [**Tools Overview**](#tools-overview)
   - [**NodeGraph Tools**](#nodegraph-tools)
     - [SmartBackdrop.py](#smartbackdroppy)
     - [NodeLabeler.py](#nodelabelerpy)
     - [AdvancedShuffle.py](#advancedshufflepy)
     - [DeleteAllBackdrops.py](#deleteallbackdropspy)
     - [CryptoMatteFixer.py](#cryptomattefixerpy)
     - [CryptoLabeler.py](#cryptolabelerpy)
   - [**Shufflers**](#shufflers)
     - [MaskCheckerPremult.py](#maskcheckerpremultpy)
     - [BatchLightShuffler.py](#batchlightshufflerpy)
     - [MaskCheckerGrade.py](#maskcheckergradepy)
   - [**Loaders**](#loaders)
     - [CameraLoader.py](#cameraloaderpy)
     - [SequenceLoader.py](#sequenceloaderpy)
     - [LoadLightningRender.py](#loadlightningrenderpy)
     - [LoadLightningRenderFromRender.py](#loadlightningrenderfromrenderpy)
     - [AppenderLoader.py](#appenderloaderpy)
     - [OpenCompFromRender.py](#opencompfromrenderpy)
     - [**NewShot Tools**](#newshot-tools)
       - [NewCompShot.py](#newcompshotpy)
       - [NewDenoiseComp.py](#newdenoisecomppy)
   - [**Else**](#else)
     - [zdefocuschecker.py](#zdefocuscheckerpy)
     - [testik.py](#testikpy)
3. [**Conclusion**](#conclusion)

---

## Installation

1. **Download** the tools package.
2. **Place** scripts in your **Nuke plugins directory**.
3. **Add** to your `init.py`:
   ```python
   nuke.pluginAddPath("/path/to/custom_tools")
   ```
4. **Restart** Nuke.

---

## Tools Overview

### NodeGraph Tools

#### **SmartBackdrop.py**

> Automatically creates a backdrop for selected nodes, enhancing node graph organization with user-defined padding and offset values.

#### **NodeLabeler.py**

> Labels and colors nodes with animated values, allowing quick identification of animatable nodes and providing visual cues for animation data.

#### **AdvancedShuffle.py**

> Enables dynamic shuffling of node connections in Nuke, offering easy vertical spacing adjustments and node identification for more efficient compositing workflows.

#### **DeleteAllBackdrops.py**

> Deletes all backdrops in the node graph, providing a quick way to clean up unnecessary backdrops.

#### **CryptoMatteFixer.py**

> Fixes CryptoMatte issues by addressing common problems such as missing IDs or broken connections, ensuring proper functionality of matte extraction.

#### **CryptoLabeler.py**

> Automatically labels CryptoMatte nodes based on the matte passes, making it easier to work with complex multi-matte workflows.

---

### Shufflers

#### **MaskCheckerPremult.py**

> Checks the premultiplied status of masks to ensure they are correctly set up for downstream operations, helping maintain consistency.

#### **BatchLightShuffler.py**

> Batch processes multiple lighting layers into different shuffles, providing an organized approach to managing complex lighting setups in Nuke.

#### **MaskCheckerGrade.py**

> Evaluates mask grades to verify the accuracy and consistency of mask layers used in compositing.

---

### Loaders

#### **CameraLoader.py**

> Loads camera data for shots into Nuke, simplifying the setup process and providing accurate camera movements for 3D integration.

#### **SequenceLoader.py**

> Loads sequences and creates read nodes for each shot, providing an efficient way to load multiple image sequences in a project.

#### **LoadLightningRender.py**

> Loads lighting render layers, creates Read nodes, and arranges them for easy setup. Also sets up Cryptomatte and premult nodes to organize the node graph.

#### **LoadLightningRenderFromRender.py**

> Loads the latest lighting render layers for a given shot in Nuke, creates Read nodes for each layer, and sets up Cryptomatte, Shuffle, and Premult node chains for easy organization.

#### **AppenderLoader.py**

> Loads sequences, creates read nodes, and generates an AppendClip node for review. It includes an easy playback function for quick reviewing of sequences.

#### **OpenCompFromRender.py**

> Opens the corresponding comp file based on a selected Read node by extracting shot and version information from the file path.

#### **NewShot Tools**

##### **NewCompShot.py**

> Sets up a new composition shot by loading project data, lighting renders, a workspace template, and updating camera settings.

##### **NewDenoiseComp.py**

> A script designed to assist with setting up a denoise comp, though it lacks a detailed description of its features.

---

### Else

#### **zdefocuschecker.py**

> Checks the ZDefocus setup for consistency, helping ensure that all settings are correctly applied.

#### **testik.py**

> A test script used for experimental purposes or quick tests during development.

---

## Conclusion

These tools represent a comprehensive approach to solving common **VFX production challenges**. They offer significant **time savings**, improved **consistency**, and enhanced **quality control** in daily tasks. As a **Technical Director**, I remain committed to refining and expanding this toolkit based on user feedback and evolving production needs.

Feel free to reach out with questions, suggestions, or specific workflow challenges that might benefit from similar custom solutions.

