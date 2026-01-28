import bpy

# ---------- USER: define your key groups here ----------
# Each entry: object name, data_path (relative to that object), dict of frame->value
# Examples:
#  - Object location: data_path = "location"
#  - Pose bone rotation quaternion: data_path = 'pose.bones["Head"].rotation_quaternion'
#  - Object rotation_euler: data_path = "rotation_euler"
#  - Material or custom prop: data_path = 'material_slots[0].material.diffuse_color' (or '["my_prop"]')
KEY_SPECS = [
    {
        "object": "Cube",
        "data_path": "location",
        "frames": {1: (0.0, 0.0, 0.0), 20: (2.0, 0.0, 0.0)}
    },
    {
        "object": "Armature",
        "data_path": 'pose.bones["Head"].rotation_quaternion',
        "frames": {1: (1.0, 0.0, 0.0, 0.0), 30: (0.9239, 0.0, 0.3827, 0.0)}
    },
    {
        "object": "Camera",
        "data_path": "rotation_euler",
        "frames": {1: (0.0, 0.0, 0.0), 50: (0.5, 0.0, 1.2)}
    }
]
# ------------------------------------------------------

def set_property_and_key(obj, data_path, frame, value):
    """
    Set the property referenced by data_path on obj to value, then insert a keyframe
    using obj.keyframe_insert(data_path=..., frame=...).
    Works for nested paths like: pose.bones["Bone"].rotation_quaternion
    """
    # Make sure object exists
    if obj is None:
        return False, "Object not found"

    # Ensure we have animation_data (keyframe_insert will create it if needed, but be explicit)
    obj.animation_data_create()

    # Split owner path from final property name (split at last '.')
    if '.' in data_path:
        owner_path, prop_name = data_path.rsplit('.', 1)
        try:
            owner = obj.path_resolve(owner_path)
        except Exception as e:
            return False, f"Failed to resolve owner path '{owner_path}': {e}"
    else:
        owner = obj
        prop_name = data_path

    # Try to set attribute on owner (this works for most RNA properties)
    try:
        setattr(owner, prop_name, value)
    except Exception:
        # fallback: for array-like values, try to write to the resolved target by slice assignment
        try:
            target = obj.path_resolve(data_path)
            # target is often a vector-like object supporting slice assignment
            target[:] = value
        except Exception as e2:
            return False, f"Failed to assign value to '{data_path}': {e2}"

    # Insert the keyframe on the *object* that owns the action (this accepts nested data_paths)
    try:
        obj.keyframe_insert(data_path=data_path, frame=frame)
    except Exception as e:
        return False, f"Failed to keyframe_insert('{data_path}') on {obj.name}: {e}"

    return True, "OK"


# Run through KEY_SPECS and apply keys
for spec in KEY_SPECS:
    obj_name = spec["object"]
    dp = spec["data_path"]
    frames = spec["frames"]

    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        print(f"[SKIP] Object '{obj_name}' not found.")
        continue

    # If setting bone quaternions, ensure correct rotation_mode on the armature's pose bones
    if 'pose.bones' in dp and 'rotation_quaternion' in dp:
        # If you need to change pose bones rotation_mode, do it before setting keys
        # (we'll set the mode on the specific bone owner)
        try:
            owner_path = dp.rsplit('.',1)[0]
            owner = obj.path_resolve(owner_path)
            # owner is a PoseBone; ensure quaternion mode
            try:
                owner.rotation_mode = 'QUATERNION'
            except Exception:
                pass
        except Exception:
            pass

    for f, v in frames.items():
        ok, msg = set_property_and_key(obj, dp, f, v)
        if not ok:
            print(f"[ERROR] {obj_name} :: {dp} @ {f} -> {msg}")
        else:
            print(f"[OK]   {obj_name} :: {dp} @ {f} = {v}")

print("Batch keying done.")
