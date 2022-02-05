import bpy
import math

"""
UV sphere scanrig setup functions
"""

# Define useful functions


def strVector3(v3):
    return str(v3.x) + "," + str(v3.y) + "," + str(v3.z)


def look_at(obj_camera, point):
    loc_camera = obj_camera.matrix_world.to_translation()

    direction = point - loc_camera
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')

    # assume we're using euler rotation
    obj_camera.rotation_euler = rot_quat.to_euler()


def create(context, objet, cameras):
    """ Creates a scanrig UV sphere setup.

    Args:
        context : the scene context
        objet : self
        cameras : camera collection

    Returns:
        int : number of cameras created
    """

    # Create a new uv sphere
    bpy.ops.mesh.primitive_uv_sphere_add(segments=objet.nbSegment, ring_count=objet.nbRing, radius=objet.domeDistance, calc_uvs=True,
                                         enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))

    # Select newly created uv sphere
    uv = bpy.context.selected_objects[0]
    # Change name
    uv.name = "uv_sphere"
    #print("Done creating " + uv.name + " at position " + strVector3(uv.location))

    # Get number of vertices
    nbCameras = len(uv.data.vertices)

    #---------- Create cam ----------#
    cam = objet.createCam("Camera", 56)

    for (i, elem) in enumerate(uv.data.vertices):
        # Get the vertices
        v = uv.data.vertices[i]

        co_final = uv.matrix_world @ v.co

        camName = f"Camera_{i}"
        current_cam = objet.createCameraObj(
            context, camName, cam, (objet.camDistance * objet.domeDistance, 0, 0), (90, 0, 90))
        current_cam.parent = cameras
        current_cam.select_set(True)
        context.view_layer.objects.active = current_cam  # (could be improved)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        current_cam.location = co_final
        bpy.context.view_layer.update()
        look_at(current_cam, uv.matrix_world.to_translation())

    # Register camera into cameras collection
    for i in range(nbCameras):
        camName = f"Camera_{i}"
        current_cam = context.scene.objects[camName]
        current_cam.parent = cameras

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    # Select the objects
    bpy.data.objects['uv_sphere'].select_set(True)
    # Delete all selected objects
    bpy.ops.object.delete()

    #---------- Create flash Light ----------#
    FlashFront = objet.createLightObj(context, "FlashFront", objet.createFlashLight(
        "FlashFront"), (0, -objet.flashDistance * objet.domeDistance, 0))
    FlashBack = objet.createLightObj(context, "FlashBack", objet.createFlashLight(
        "FlashBack"), (0, objet.flashDistance * objet.domeDistance, 0))
    FlashLeft = objet.createLightObj(context, "FlashLeft", objet.createFlashLight(
        "FlashLeft"), (objet.flashDistance * objet.domeDistance, 0, 0))
    FlashRight = objet.createLightObj(context, "FlashRight", objet.createFlashLight(
        "FlashRight"), (-objet.flashDistance * objet.domeDistance, 0, 0))
    FlashTop = objet.createLightObj(context, "FlashTop", objet.createFlashLight(
        "FlashTop"), (0, 0, objet.flashDistance * objet.domeDistance))
    FlashBottom = objet.createLightObj(context, "FlashBottom", objet.createFlashLight(
        "FlashBottom"), (0, 0, -objet.flashDistance * objet.domeDistance))

    #---------- Create Flash Light Collection ----------#
    flashLights = bpy.data.objects.new(
        'FlashLights', None)  # None for empty object
    flashLights.location = (0, 0, 0)
    flashLights.empty_display_type = 'PLAIN_AXES'

    objet.linkToScanRigCollection(flashLights)
    # Relinking
    FlashFront.parent = FlashBack.parent = FlashLeft.parent = FlashRight.parent = FlashTop.parent = FlashBottom.parent = flashLights

    #---------- Create Led light ----------#
    LedFront = objet.createLightObj(context, "LedFront", objet.createLedLight(
        "LedFront"), (0, -objet.ledDistance * objet.domeDistance, 0), (90, 0, 0))
    LedBack = objet.createLightObj(context, "LedBack", objet.createLedLight(
        "LedBack"), (0, objet.ledDistance * objet.domeDistance, 0), (-90, 0, 0))
    LedLeft = objet.createLightObj(context, "LedLeft", objet.createLedLight(
        "LedLeft"), (objet.ledDistance * objet.domeDistance, 0, 0), (0, 90, 0))
    LedRight = objet.createLightObj(context, "LedRight", objet.createLedLight(
        "LedRight"), (-objet.ledDistance * objet.domeDistance, 0, 0), (0, -90, 0))
    LedTop = objet.createLightObj(context, "LedTop", objet.createLedLight(
        "LedTop"), (0, 0, objet.ledDistance * objet.domeDistance), (0, 0, 0))
    LedBottom = objet.createLightObj(context, "LedBottom", objet.createLedLight(
        "LedBottom"), (0, 0, -objet.ledDistance * objet.domeDistance), (180, 0, 0))

    #---------- Rotate Led light by 37.5 degrees ----------#
    ledLights = bpy.data.objects.new(
        'LedLights', None)  # None for empty object
    ledLights.location = (0, 0, 0)
    ledLights.empty_display_type = 'PLAIN_AXES'

    objet.linkToScanRigCollection(ledLights)
    # Relinking
    LedFront.parent = LedBack.parent = LedLeft.parent = LedRight.parent = LedTop.parent = LedBottom.parent = ledLights
    ledLights.rotation_euler[2] = math.radians(objet.ledAngle)

    # done
    print("Done")

    return nbCameras
