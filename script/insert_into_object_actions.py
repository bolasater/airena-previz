import bpy

obj = bpy.data.objects['Cube']

# Make or get an Action
act = bpy.data.actions.get("MyMergedAction") or bpy.data.actions.new("MyMergedAction")

# Ensure the object has animation_data and assign the Action
obj.animation_data_create()
obj.animation_data.action = act

# Now keyframe_insert writes into act
obj.location = (1.0, 2.0, 3.0)
obj.keyframe_insert(data_path="location", frame=1)
