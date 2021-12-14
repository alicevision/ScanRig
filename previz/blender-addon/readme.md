<!-- omit in toc -->
# ScanRig Previsualization with Blender

<!-- omit in toc -->
## Table of Contents

- [Prerequisites](#prerequisites)
- [How to install](#how-to-install)
- [How to use](#how-to-use)
  - [Example](#example)

## Prerequisites

- You must have a version of Blender 2.8+.
- You must have the archive *scanRigAddon.zip* somewhere on your hard drive.

## How to install

- Compress the *scanRigAddon* folder in .zip format
- Open Blender and go to *Edit/Preferences*.
- Go into the *Add-ons* tab and press the *Install...* button.
- Go into the directory containing the archive *scanRigAddon.zip*.
- Select the file and press *Install Add-on from File...*.
- You should see a new line inside the Add-ons viewer with *Generic: ScanRig Addon* as a title. You can read the description by pressing the little arrow and you must check the box to enable the add-on.
- Then you can click on the little hamburger menu on the bottom left and choose *Save Preferences*.
- Now, you can close the *Preferences* window.

## How to use

- Inside the 3D Viewer, you can see a sidebar menu on the right. If not, you can go into the *View* menu (on top of the viewer) and check *Sidebar*.
- Now, you can access to the *ScanRig* tab from this *Sidebar*.

There are several buttons you can play with.

- **Set Project Settings:** Set the Blender project to correspond to the FSCAM_CU135 specifications and to optimize the rendering (Cycles with GPU, etc). On the bottom left of the 3D Viewer, you should see a *Set Project Settings* window you can expand. Inside, you can control different render settings.
- **Clean The Scene:** Remove absolutely every object of the scene.
- **Setup The Scene:** Create cameras and lights to correspond to whichever ScanRig model is chosen in the <ins>Camera Dome Shape</ins> scroll menu above (*Sphere*, *Icosahedron* or *UV Sphere*). When you press this button, several options will appear.

  -  On the bottom left of the 3D Viewer, you should see a *Setup The Scene* window you can expand. Inside, you can control the location of the elements.
  -  In the *ScanRig* panel, you can now define several more options:
        - The ***Photometry Management*** options (<ins>only used if the Camera Dome Shape is set to *Sphere*</ins>):
          - **Rotation Angle:** Angle (in degrees) separating the take of two consecutive pictures.
          - **Photometry Step Divider:** If 1, photometry will be done on each rotation step. If 2, it will be done one step out of 2, etc.
        - The ***Render Management*** options:
          - **Render mode:** Here, you can choose if you want to render only with Ambiant lights, only with Flash lights (photometry) or with both.
          - Several tick boxes corresponding to the different types of image maps you want to render (*Albedo*, *Depth*, *Normal*, *Id* or *Basic* maps).
          - **Start Render:** Start the rendering process. Please, make sure to open the console (on Windows, you can do it inside *Window/Toggle System Console* - on Linux/OSX, it is better to launch Blender directly with the terminal). When a camera will have completed its task, you will have to tell if you want to continue the process or not (with the console).

:construction: Before launching the render, you **have to save** the Blender file. If you do not, the script will crash because it needs the project to be saved somewhere to create a folder *img* next to it for saving the renders.

### Example

- Rotation Angle = 15
- Photometry Step Divider = 3
- Render mode = Ambiant & Photometry
- Tickboxes: Depth & Basic

Result:

- Cameras will take 24 ambiant lights pictures (one on each **15**° of the revolution).
- Cameras will take 6x8 photometry lights pictures (six (X, -X, Y, -Y, Z, -Z) on each **3**x**15**° of the revolution).
- Cameras will each time take a picture of the **Depth** map and a picture of the **Basic** map.
