<div align="center">
  <img src="https://github.com/alicevision/ScanRig/wiki/img/logo.png" alt="Logo" width="200px">
  
  > Multi-Cameras/Lighting Acquisition Setup for Photogrammetry.
  > See [Meshroom](https://github.com/alicevision/meshroom) for 3D Reconstruction.
  
  [Wiki](https://github.com/alicevision/ScanRig/wiki) | [Supplies](https://github.com/alicevision/ScanRig/wiki/Supplies)
  
  <img src="https://github.com/alicevision/ScanRig/wiki/img/3d/full-rig.png" alt="Lighting stand" width="400px">
</div>

## Status

Early beginning of development.

## Install

```
git clone https://github.com/alicevision/ScanRig.git
# Create a dedicated virtual environment
python -m venv ScanRigPyEnv
# Install opencv in this environment
ScanRigPyEnv/Scripts/pip install opencv-python
```


## Launch

```
# Launch the acquisition script in the newly created environment
ScanRigPyEnv/Scripts/python ScanRig/bin/multiCameraCapture.py --help
```


## License

The project is released under MPLv2, see [**LICENSE.md**](LICENSE.md).
