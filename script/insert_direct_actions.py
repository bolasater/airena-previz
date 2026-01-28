act = bpy.data.actions.get("MyDirectAction") or bpy.data.actions.new("MyDirectAction")

# create an fcurve for object location.x
fc = act.fcurves.new(data_path="location", index=0)

# insert a keyframe point at frame 1, value 1.0
kp = fc.keyframe_points.insert(frame=1, value=1.0)
kp.interpolation = 'BEZIER'
fc.update()

# Later, assign the action to an object (if desired)
obj = bpy.data.objects['Cube']
obj.animation_data_create()
obj.animation_data.action = act


