import bpy
import math
import mathutils


# Define useful functions
def strVector3( v3 ):
    return str(v3.x) + "," + str(v3.y) + "," + str(v3.z)

def look_at(obj_camera, point):
    loc_camera = obj_camera.matrix_world.to_translation()

    direction = point - loc_camera
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')
    
    # assume we're using euler rotation
    obj_camera.rotation_euler = rot_quat.to_euler()


# Creating cameras collection
#cameras = bpy.data.objects.new('Cameras', None) # None for empty object
#cameras.location = (0,0,0)
#cameras.empty_display_type = 'PLAIN_AXES'
#
#camera_data = bpy.data.cameras.new(name='Camera')
#camera_object = bpy.data.objects.new('Camera', camera_data)
#bpy.context.scene.collection.objects.link(camera_object)

def create(context, objet, cameras):

    # Create a new icosahedron
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=objet.nbSubdiv, radius=objet.domeDistance, calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))

    # Select newly created icosahedron
    ico = bpy.context.selected_objects[0]
    # Change name
    ico.name = "ico_sphere"
    #print("Done creating " + ico.name + " at position " + strVector3(ico.location))
    
    # Change its location
    #ico.location = (0.0, 5.0, 0.0)

    # Get number of vertices
    nbCameras = len(ico.data.vertices)

    #---------- Create cam ----------#
    cam = objet.createCam("Camera", 56)

    for (i, elem) in enumerate(ico.data.vertices):
        # Get the vertices
        v = ico.data.vertices[i]

        co_final = ico.matrix_world @ v.co

        # now we can view the location by applying it to an object
        #obj_empty = bpy.data.objects.new("Test", None)
        #bpy.context.collection.objects.link(obj_empty)
        
        # Create the camera
        # camName = f"Camera_{i}"
        # current_cam = bpy.data.cameras.new(camName )
        # # Create the camera object
        # current_cam_obj = bpy.data.objects.new(camName, current_cam)
        
        camName = f"Camera_{i}"
        current_cam = objet.createCameraObj(context, camName, cam, (objet.camDistance * objet.domeDistance, 0, 0), (90, 0, 90))
        current_cam.parent = cameras
        current_cam.select_set(True)
        context.view_layer.objects.active  = current_cam # (could be improved)
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

        #obj_empty.location = co_final
        current_cam.location = co_final
        bpy.context.view_layer.update()
        look_at(current_cam, ico.matrix_world.to_translation())

    # Register camera into cameras collection
    for i in range(nbCameras):
        camName = f"Camera_{i}"
        current_cam = context.scene.objects[camName]
        current_cam.parent = cameras


    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    # Select the objects
    bpy.data.objects['ico_sphere'].select_set(True)
    # Delete all selected objects
    bpy.ops.object.delete() 

    #---------- Create flash Light ----------#
    flashLight = objet.createFlashLight("FlashLight")
    FlashFront = objet.createLightObj(context, "FlashFront", flashLight, (0, -objet.flashDistance * objet.domeDistance, 0))
    FlashBack = objet.createLightObj(context, "FlashBack", flashLight, (0, objet.flashDistance * objet.domeDistance, 0))
    FlashLeft = objet.createLightObj(context, "FlashLeft", flashLight, (objet.flashDistance * objet.domeDistance, 0, 0))
    FlashRight = objet.createLightObj(context, "FlashRight", flashLight, (-objet.flashDistance * objet.domeDistance, 0, 0))
    FlashTop = objet.createLightObj(context, "FlashTop", flashLight, (0, 0, objet.flashDistance * objet.domeDistance))
    FlashBottom = objet.createLightObj(context, "FlashBottom", flashLight, (0, 0, -objet.flashDistance * objet.domeDistance))

    #---------- Create Flash Light Collection ----------#
    flashLights = bpy.data.objects.new('FlashLights', None) # None for empty object
    flashLights.location = (0,0,0)
    flashLights.empty_display_type = 'PLAIN_AXES'

    objet.linkToScanRigCollection(flashLights)
    # Relinking
    FlashFront.parent = FlashBack.parent = FlashLeft.parent = FlashRight.parent = FlashTop.parent = FlashBottom.parent = flashLights

    #---------- Create Led light ----------#
    ledlight = objet.createLedLight("Ledlight")
    LedFront = objet.createLightObj(context, "LedFront", ledlight, (0, -objet.ledDistance * objet.domeDistance, 0), (90, 0, 0))
    LedBack = objet.createLightObj(context, "LedBack", ledlight, (0, objet.ledDistance * objet.domeDistance, 0), (-90, 0, 0))
    LedLeft = objet.createLightObj(context, "LedLeft", ledlight, (objet.ledDistance * objet.domeDistance, 0, 0), (0, 90, 0))
    LedRight = objet.createLightObj(context, "LedRight", ledlight, (-objet.ledDistance * objet.domeDistance, 0, 0), (0, -90, 0))
    LedTop = objet.createLightObj(context, "LedTop", ledlight, (0, 0, objet.ledDistance * objet.domeDistance), (0, 0, 0))
    LedBottom = objet.createLightObj(context, "LedBottom", ledlight, (0, 0, -objet.ledDistance * objet.domeDistance), (180, 0, 0))

    #---------- Rotate Led light by 37.5 degrees ----------#
    ledLights = bpy.data.objects.new('LedLights', None) # None for empty object
    ledLights.location = (0,0,0)
    ledLights.empty_display_type = 'PLAIN_AXES'

    objet.linkToScanRigCollection(ledLights)
    # Relinking
    LedFront.parent = LedBack.parent = LedLeft.parent = LedRight.parent = LedTop.parent = LedBottom.parent = ledLights
    ledLights.rotation_euler[2] = math.radians(objet.ledAngle)

    # done
    print("Done")

    return nbCameras
