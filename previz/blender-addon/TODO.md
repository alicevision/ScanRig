<!-- omit in toc -->
# List of improvements to add

<!-- omit in toc -->
## Table of Contents

- [EXIF metadata management](#exif-metadata-management)
- [JSON file generation for OpenGL](#json-file-generation-for-opengl)
- [Various improvements](#various-improvements)

#
## EXIF metadata management
* Add EXIF information to the images or find a way to export the data.
    * study OpenimageIO --> support EXIF + format .exr (https://sites.google.com/site/openimageio/home) 
    https://openimageio.readthedocs.io/en/latest/pythonbindings.html 
* If OpenImage is not installed, don't propose to use its format (*add export formats management in UI*).

#
## JSON file generation for OpenGL
* Generate the calibration poses (camera positions and rotations) of the dome so that we can run with known poses for OpenGL.
    * challenging -> python scripting to export the poses (OpenGL ref system hell) into a sfm format.
    * example : List all the cameras in a json file when we render the dome.
        ```
        camera_id : 0
        centre : [x,y,z]
        rotation : [3x3]
        angleAxis2rotationMatrix
        ```
    * https://www.geeksforgeeks.org/how-to-convert-python-dictionary-to-json/
    * https://docs.python.org/fr/3/library/json.html  (.dumps method)
    
#
## Various improvements
* Generate different trajectories of cameras around the object.
#