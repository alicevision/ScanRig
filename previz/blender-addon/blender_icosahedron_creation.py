import bpy

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

def create():

    # Create a new icosahedron
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.0, calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(10.0, 10.0, 10.0))

    # Select newly created icosahedron
    ico = bpy.context.selected_objects[0]
    # Change name
    ico.name = "ico_sphere"
    #print("Done creating " + ico.name + " at position " + strVector3(ico.location))
    
    # Change its location
    #ico.location = (0.0, 5.0, 0.0)

    # for (i,elem) in enumerate(ico.data.vertices)
    for i in range(12):
        # Get the vertices
        v = ico.data.vertices[i]

        co_final = ico.matrix_world @ v.co

        # now we can view the location by applying it to an object
        #obj_empty = bpy.data.objects.new("Test", None)
        #bpy.context.collection.objects.link(obj_empty)
        
        # Create the camera
        camName = f"Camera_{i}"
        current_cam = bpy.data.cameras.new(camName )
        current_cam.lens = 18
        # Create the camera object
        current_cam_obj = bpy.data.objects.new(camName, current_cam)
        
        #current_cam = self.__createCameraObj(context, camName, cam, (self.camDistance * self.domeDistance, 0, 0), (90, 0, 90))
        #current_cam.parent = cameras
        
        #obj_empty.location = co_final
        bpy.context.scene.collection.objects.link(current_cam_obj)
        current_cam_obj.location = co_final
        bpy.context.view_layer.update()
        look_at(current_cam_obj, ico.matrix_world.to_translation())

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    # Select the objects
    bpy.data.objects['ico_sphere'].select_set(True)
    # Delete all selected objects
    bpy.ops.object.delete() 

    # done
    print("Done")
