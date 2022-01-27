import bpy
import math

"""
Sphere scanrig setup functions
"""

def create(context, objet, cameras):
    """ Create a scanrig sphere setup.

    Args:
        context : the scene context
        objet : self
        cameras : camera collection
    """

    # Computing the angle between cams
    deltaAngle = (objet.stopAngle - objet.startAngle)/(objet.nbCamera -1)

    #---------- Create cam ----------#
    cam = objet.createCam("Camera", 56)

    for i in range(objet.nbCamera):
        camName = f"Camera_{i}"
        camAngle = objet.startAngle + i*deltaAngle
        current_cam = objet.createCameraObj(context, camName, cam, (objet.camDistance * objet.domeDistance, 0, 0), (90, 0, 90))
        current_cam.parent = cameras
        cameras.rotation_euler[1] = math.radians(camAngle)
        current_cam.select_set(True)
        context.view_layer.objects.active = current_cam # (could be improved)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

    cameras.rotation_euler[1] = math.radians(0)
    for i in range(objet.nbCamera):
        camName = f"Camera_{i}"
        current_cam = context.scene.objects[camName]
        current_cam.parent = cameras
    
    #---------- Create flash Light ----------#
    FlashFront = objet.createLightObj(context, "FlashFront", objet.createFlashLight("FlashFront"), (0, -objet.flashDistance * objet.domeDistance, 0))
    FlashBack = objet.createLightObj(context, "FlashBack", objet.createFlashLight("FlashBack"), (0, objet.flashDistance * objet.domeDistance, 0))
    FlashLeft = objet.createLightObj(context, "FlashLeft", objet.createFlashLight("FlashLeft"), (objet.flashDistance * objet.domeDistance, 0, 0))
    FlashRight = objet.createLightObj(context, "FlashRight", objet.createFlashLight("FlashRight"), (-objet.flashDistance * objet.domeDistance, 0, 0))
    FlashTop = objet.createLightObj(context, "FlashTop", objet.createFlashLight("FlashTop"), (0, 0, objet.flashDistance * objet.domeDistance))
    FlashBottom = objet.createLightObj(context, "FlashBottom", objet.createFlashLight("FlashBottom"), (0, 0, -objet.flashDistance * objet.domeDistance))

    #---------- Create Flash Light Collection ----------#
    flashLights = bpy.data.objects.new('FlashLights', None) # None for empty object
    flashLights.location = (0, 0, 0)
    flashLights.empty_display_type = 'PLAIN_AXES'

    objet.linkToScanRigCollection(flashLights)
    # Relinking
    FlashFront.parent = FlashBack.parent = FlashLeft.parent = FlashRight.parent = FlashTop.parent = FlashBottom.parent = flashLights

    #---------- Create Led light ----------#
    LedFront = objet.createLightObj(context, "LedFront", objet.createLedLight("LedFront"), (0, -objet.ledDistance * objet.domeDistance, 0), (90, 0, 0))
    LedBack = objet.createLightObj(context, "LedBack", objet.createLedLight("LedBack"), (0, objet.ledDistance * objet.domeDistance, 0), (-90, 0, 0))
    LedLeft = objet.createLightObj(context, "LedLeft", objet.createLedLight("LedLeft"), (objet.ledDistance * objet.domeDistance, 0, 0), (0, 90, 0))
    LedRight = objet.createLightObj(context, "LedRight", objet.createLedLight("LedRight"), (-objet.ledDistance * objet.domeDistance, 0, 0), (0, -90, 0))
    LedTop = objet.createLightObj(context, "LedTop", objet.createLedLight("LedTop"), (0, 0, objet.ledDistance * objet.domeDistance), (0, 0, 0))
    LedBottom = objet.createLightObj(context, "LedBottom", objet.createLedLight("LedBottom"), (0, 0, -objet.ledDistance * objet.domeDistance), (180, 0, 0))

    #---------- Rotate Led light by 37.5 degrees ----------#
    ledLights = bpy.data.objects.new('LedLights', None) # None for empty object
    ledLights.location = (0, 0, 0)
    ledLights.empty_display_type = 'PLAIN_AXES'

    objet.linkToScanRigCollection(ledLights)
    # Relinking
    LedFront.parent = LedBack.parent = LedLeft.parent = LedRight.parent = LedTop.parent = LedBottom.parent = ledLights
    ledLights.rotation_euler[2] = math.radians(objet.ledAngle)
