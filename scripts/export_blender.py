import bpy
import sys
from pathlib import Path

bpy.ops.wm.open_mainfile(filepath=sys.argv[1])
context = bpy.context
scene = context.scene
viewlayer = context.view_layer

class Entry:
    def __init__(
            self,
            col_name,
            stl_name,
            axis_up='Z',
            axis_forward='Y',
            merge=False,
            split=False,
            multiple=False,
            rotate=False,
            tolerance=False,
            mirror=False,
        ):
        self.col_name = col_name  # Collection name.
        self.stl_name_base = stl_name
        self.stl_name = stl_name
        self.axis_up = axis_up
        self.axis_forward = axis_forward
        self.merge = merge  # Export all the objects in the collection merged.
        self.multiple = multiple  # Multiple individual exports in the collection.
        self.split = split
        self.rotate = rotate
        self.tolerance = tolerance
        self.tight = tolerance  # Export tight variant.
        self.loose = tolerance  # Export loose variant.
        self.mirror = mirror

    @staticmethod
    def find(name):
        for entry in entries:
            if entry.col_name == name:
                return entry

    @property
    def objects(self):
        return [o for o in scene.objects if o.type == 'MESH']

    def process(self, variant=False):
        bpy.ops.object.select_all(action='DESELECT')
        if not variant and self.tolerance:
            if self.tight:
                self.process_tight()
            if self.loose:
                self.process_loose()
        for ob in self.objects:
            if not ob.visible_get(): continue
            viewlayer.objects.active = ob
            ob.select_set(True)
            if self.rotate:
                self.do_rotate(ob)
            if self.split:
                self.do_split(ob)
            if not self.merge:
                if self.multiple:
                    subentry = Entry.find(ob.name)
                    subentry.export()
                else:
                    self.export()
                ob.select_set(False)
        if self.merge:
            self.export()
        if not variant and self.mirror:
            self.process_mirror()

    def do_rotate(self, ob):
        for mod in ob.modifiers:
            if 'rotation' in mod.name:
                mod.show_viewport = True

    def do_split(self, ob):
        for mod in ob.modifiers:
            if 'instance' in mod.name:
                mod.show_viewport = False

    def process_tight(self):
        for ob in self.objects:
            for mod in ob.modifiers:
                if 'loose' in mod.name:
                    mod.show_viewport = False
                if 'tight' in mod.name:
                    mod.show_viewport = True
        self.stl_name = f'{entry.stl_name_base}_tight'
        self.tight = False
        self.process(True)

    def process_loose(self):
        for ob in self.objects:
            for mod in ob.modifiers:
                if 'loose' in mod.name:
                    mod.show_viewport = True
                if 'tight' in mod.name:
                    mod.show_viewport = False
        self.stl_name = f'{entry.stl_name_base}_loose'
        self.loose = False
        self.process(True)

    def process_mirror(self):
        for ob in self.objects:
            for mod in ob.modifiers:
                if 'Mirror print' in mod.name:
                    mod.show_viewport = True
        self.stl_name = self.stl_name.replace('R', 'L')
        self.mirror = False
        self.process(True)

    def export(self):
        root = Path(bpy.path.abspath("//")).parent
        path = root / 'stl' / f'{self.stl_name}.stl'
        bpy.ops.wm.stl_export(
            filepath=str(path),
            export_selected_objects=True,
            up_axis=self.axis_up,
            forward_axis=self.axis_forward
        )


entries = [
    Entry('Case front',       '015mm_front'),
    Entry('Case back',        '015mm_back', 'NEGATIVE_Z'),
    Entry('Case cover',       '015mm_cover'),
    Entry('R1',               '015mm_trigger_R1', split=True, mirror=True),
    Entry('R2',               '015mm_trigger_R2', 'NEGATIVE_Z', split=True, mirror=True),
    Entry('R4',               '015mm_trigger_R4', 'NEGATIVE_Y', 'NEGATIVE_Z', split=True, mirror=True),
    Entry('Home',             '007mm_home'),
    Entry('Abxy',             '007mm_abxy_4x', split=True),
    Entry('Dpad',             '007mm_dpad_4x', split=True),
    Entry('Select',           '007mm_select_4x', split=True),
    Entry('Thumbstick',       '007mm_thumbstick_2x', tolerance=True),
    Entry('Anchor',           '015mm_anchors_2x', 'NEGATIVE_Z', split=True),
    Entry('Soldering helper', '020mm_solderstand', 'NEGATIVE_Z', merge=True),
    Entry('Wheel',            '015mm_scrollwheel',),
    Entry('Wheel shaft R',    '007mm_scrollwheel_shaft'),
    Entry('Wheel support',    '015mm_scrollwheel_support'),
    Entry('Scrollwheel',      None, multiple=True),
]

for collection in bpy.data.collections:
    entry = Entry.find(collection.name)
    entry.process()
    break
