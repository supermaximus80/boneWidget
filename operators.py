import bpy

from .functions import findMatchBones
from .functions import fromWidgetFindBone
from .functions import findMirrorObject
from .functions import symmetrizeWidget
from .functions import boneMatrix
from .functions import createWidget
from .functions import editWidget
from .functions import returnToArmature
from .functions import addRemoveWidgets
from .functions import readWidgets
from .functions import objectDataToDico
from .functions import get_collection
from bpy.types import Operator
from bpy.props import FloatProperty, BoolProperty, FloatVectorProperty


class bw_createWidget(bpy.types.Operator):
    """Creates a widget for selected bone"""
    bl_idname = "bonewidget.create_widget"
    bl_label = "Create"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.mode == 'POSE')

    relative_size: BoolProperty(
        name="Relative size",
        default=True,
        description="Widget size proportionnal to bone size"
    )

    global_size: FloatProperty(
        name="Global Size",
        default=1.0,
        description="Global Size"
    )

    slide: FloatProperty(
        name="Slide",
        default=0.0,
        subtype='DISTANCE',
        unit='LENGTH',
        description="slide widget along y axis"
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, "relative_size")
        row = layout.row(align=True)
        row.prop(self, "global_size", expand=False)
        row = layout.row(align=True)
        row.prop(self, "slide")

    def execute(self, context):
        wgts = readWidgets()
        for bone in bpy.context.selected_pose_bones:
            createWidget(bone, wgts[context.scene.widget_list], self.relative_size, self.global_size, [
                         1, 1, 1], self.slide, get_collection(context))

        return {'FINISHED'}


class bw_editWidget(bpy.types.Operator):
    """Edit the widget for selected bone"""
    bl_idname = "bonewidget.edit_widget"
    bl_label = "Edit"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.pose)

    def execute(self, context):
        editWidget(context.active_pose_bone)
        return {'FINISHED'}


class bw_returnToArmature(bpy.types.Operator):
    """Switch back to the armature"""
    bl_idname = "bonewidget.return_to_armature"
    bl_label = "Return to armature"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'MESH'
                and context.object.mode in ['EDIT', 'OBJECT'])

    def execute(self, context):
        if fromWidgetFindBone(bpy.context.object):
            returnToArmature(bpy.context.object)

        else:
            self.report({'INFO'}, 'Object is not a bone widget')

        return {'FINISHED'}


class bw_MatchBoneTransforms(bpy.types.Operator):
    """Match the widget to the bone transforms"""
    bl_idname = "bonewidget.match_bone_transforms"
    bl_label = "Match bone transforms"

    def execute(self, context):
        if bpy.context.mode == "POSE":
            for bone in bpy.context.selected_pose_bones:
                if bone.custom_shape_transform and bone.custom_shape:
                    boneMatrix(bone.custom_shape, bone.custom_shape_transform)
                elif bone.custom_shape:
                    boneMatrix(bone.custom_shape, bone)

        else:
            for ob in bpy.context.selected_objects:
                if ob.type == 'MESH':
                    matchBone = fromWidgetFindBone(ob)
                    if matchBone:
                        if matchBone.custom_shape_transform:
                            boneMatrix(ob, matchBone.custom_shape_transform)
                        else:
                            boneMatrix(ob, matchBone)

        return {'FINISHED'}


class bw_match_symmetrizeShape(bpy.types.Operator):
    """Symmetrize to the opposite side, if it is named with a .L or .R"""
    bl_idname = "bonewidget.symmetrize_shape"
    bl_label = "Symmetrize"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        collection = get_collection(context)
        widgetsAndBones = findMatchBones()[0]
        activeObject = findMatchBones()[1]
        widgetsAndBones = findMatchBones()[0]

        for bone in widgetsAndBones:
            if activeObject.name.endswith("L"):
                if bone.name.endswith("L") and widgetsAndBones[bone]:
                    symmetrizeWidget(bone, collection)
            else:
                if bone.name.endswith("R") and widgetsAndBones[bone]:
                    symmetrizeWidget(bone, collection)

        return {'FINISHED'}


class bw_addWidgets(bpy.types.Operator):
    """Add selected mesh object to Bone Widget Library"""
    bl_idname = "bonewidget.add_widgets"
    bl_label = "Add Widgets"

    def execute(self, context):
        objects = []
        if bpy.context.mode == "POSE":
            for bone in bpy.context.selected_pose_bones:
                objects.append(bone.custom_shape)
        else:
            for ob in bpy.context.selected_objects:
                if ob.type == 'MESH':
                    objects.append(ob)

        if not objects:
            self.report({'INFO'}, 'Select Meshes or Pose_bones')

        addRemoveWidgets(context, "add", bpy.types.Scene.widget_list[1]['items'], objects)

        return {'FINISHED'}


class bw_removeWidgets(bpy.types.Operator):
    """Remove selected widget object from the Bone Widget Library"""
    bl_idname = "bonewidget.remove_widgets"
    bl_label = "Remove Widgets"

    def execute(self, context):
        objects = bpy.context.scene.widget_list
        addRemoveWidgets(context, "remove", bpy.types.Scene.widget_list[1]['items'], objects)
        return {'FINISHED'}


classes = (
    bw_removeWidgets,
    bw_addWidgets,
    bw_match_symmetrizeShape,
    bw_MatchBoneTransforms,
    bw_returnToArmature,
    bw_editWidget,
    bw_createWidget,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
