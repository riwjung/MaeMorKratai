"""Shared pieces for The Fool at work: palette, office/meeting/colosseum sets, the plush lion "งาน",
pose and camera helpers.  World units follow the rabbit rig (a standing rabbit is ~4.15 tall).
Runs in the live Blender (via the HiggsBlender connector) and in headless Blender alike."""
import bpy, math, random
from math import sin, cos, pi
from pathlib import Path
from mathutils import Vector
from characters import *

P = Path(__file__).resolve().parent.parent
FPS = 24
W, H = 720, 1280

EXTRA = {
 'shirt_blue': ('A9C8E8', .7), 'shirt_pink': ('F2BFCF', .7), 'shirt_mint': ('B5DEC8', .7), 'shirt_yellow': ('F3DFA0', .7),
 'shirt_lilac': ('C9B8E6', .7), 'floor': ('CDBFD9', .8), 'wall': ('EEE3F2', .85), 'desk': ('F6EDE0', .5), 'desk_leg': ('B9A6C9', .5),
 'frame': ('5B5470', .4), 'screen': ('BFE3F2', .3, 0, 1.2), 'screen_dim': ('8FA9C4', .3, 0, .35), 'paper': ('FAF6EC', .8),
 'sticky_y': ('F7DD72', .7), 'sticky_p': ('F5A3B8', .7), 'sticky_b': ('9ED3F0', .7), 'folder_b': ('7FA6D9', .6),
 'folder_o': ('F0A86C', .6), 'folder_g': ('8CC59A', .6), 'chair': ('6F6385', .45), 'chair_seat': ('8E7FB0', .7),
 'sand': ('E8C98F', .95), 'stone': ('EADBC2', .85), 'stone_dark': ('C9AE8A', .85), 'banner_red': ('C8574F', .7),
 'banner_purple': ('7A5AA6', .7), 'lion': ('E9A54B', .8), 'lion_belly': ('F6D7A0', .8), 'lion_nose': ('6A3B2E', .3),
 'deadline': ('D9443A', .5), 'toga': ('FBF7EE', .8), 'laurel': ('7BA56A', .6), 'grape': ('7D4BA6', .3),
 'board': ('FFFFFF', .25), 'marker_b': ('3E6FB0', .5), 'marker_r': ('D0504A', .5), 'clock_face': ('FFFDF7', .5),
 'clock_rim': ('B48CD6', .4), 'hands': ('3B3048', .4), 'phones': ('F28CA8', .4), 'plant': ('7FB58A', .7), 'pot': ('E5A88C', .7),
 'popup': ('FFD86B', .4, 0, 1.0), 'sky_morning': ('CFE8FF', .5, 0, 1.4), 'tray': ('B9A6C9', .5),
 'box': ('D9B486', .85), 'box_dark': ('C19A6B', .85), 'coffee': ('4A2C1D', .25), 'mug': ('F6F1E6', .3),
 'rail': ('E09AC0', .55), 'toy_bar': ('8FD0E8', .45), 'steel': ('C9C3D6', .35, .6),
}


def palette_fo():
    M = palette()
    for k, a in EXTRA.items():
        M[k] = material(k, *a)
    return M


# ---------------------------------------------------------------- scene, lights, camera

def setup_scene(name, nframes):
    if bpy.app.background:
        sc = bpy.context.scene
        for o in list(sc.objects):
            bpy.data.objects.remove(o)
        sc.name = name
    else:
        old = bpy.data.scenes.get(name)
        if old:
            for o in list(old.objects):
                bpy.data.objects.remove(o)
            bpy.data.scenes.remove(old)
        sc = bpy.data.scenes.new(name)
        bpy.context.window.scene = sc
    r = sc.render
    r.engine = 'BLENDER_EEVEE'; r.resolution_x, r.resolution_y, r.resolution_percentage = W, H, 100
    r.fps = FPS; sc.frame_start, sc.frame_end = 1, nframes
    sc.eevee.taa_render_samples = 16; sc.eevee.use_raytracing = False
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'; sc.view_settings.exposure = 0
    if not sc.world:
        sc.world = bpy.data.worlds.new(name + ' world')
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes.get('Background')
    bg.inputs[0].default_value = (*linear('D9CCE6'), 1); bg.inputs[1].default_value = .55
    r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGB'
    return sc


def light(name, kind, loc, target, energy, col='FFF1DE', size=4, angle=10):
    d = bpy.data.lights.new(name, kind); o = bpy.data.objects.new(name, d); bpy.context.collection.objects.link(o)
    o.location = loc; d.energy = energy; d.color = linear(col)
    if kind == 'AREA':
        d.shape = 'DISK'; d.size = size
    if kind == 'SUN':
        d.angle = math.radians(angle)
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return o


def soft_rig(target=(0, 0, 2), warm='FFE6C7', key=1200, fill=500, sun=2.5, sun_from=(-6, -8, 10)):
    """Plush look: warm sun key from front-left, big cool fill, rim from behind."""
    t = Vector(target)
    light('LGT_key_sun', 'SUN', t + Vector(sun_from), t, sun, warm, angle=12)
    light('LGT_fill', 'AREA', t + Vector((7, -6, 4)), t, fill, 'DCD8FF', size=8)
    light('LGT_rim', 'AREA', t + Vector((-2, 7, 6)), t, key, 'FFD6A8', size=5)


def camera(sc, lens=26, fstop=2.2):
    d = bpy.data.cameras.new('CAM'); cam = bpy.data.objects.new('CAM', d); bpy.context.collection.objects.link(cam)
    tgt = bpy.data.objects.new('CAM_target', None); bpy.context.collection.objects.link(tgt)
    c = cam.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    d.lens = lens; d.sensor_width = 36; d.clip_start = .05; d.clip_end = 400
    d.dof.use_dof = True; d.dof.focus_object = tgt; d.dof.aperture_fstop = fstop
    sc.camera = cam
    return cam, tgt


def cam_key(cam, tgt, f, pos, look, lens=None):
    cam.location = pos; tgt.location = look
    cam.keyframe_insert('location', frame=f); tgt.keyframe_insert('location', frame=f)
    if lens:
        cam.data.lens = lens; cam.data.keyframe_insert('lens', frame=f)


# ---------------------------------------------------------------- rig posing

IDLE = {'arm.L': (-.15, 0, 0), 'arm.R': (-.15, 0, 0)}
SIT = {'leg.L': (-1.35, 0, 0), 'leg.R': (-1.35, 0, 0), 'arm.L': (-.6, 0, 0), 'arm.R': (-.6, 0, 0)}


def pose(rig, f, base=IDLE, **rot):
    """Key every bone. Names use '_' for '.', e.g. arm_L=(x, y, z)."""
    want = dict(base)
    for k, v in rot.items():
        want[k.replace('_L', '.L').replace('_R', '.R')] = v
    for b in rig.pose.bones:
        b.rotation_euler = want.get(b.name, (0, 0, 0))
        b.keyframe_insert('rotation_euler', frame=f)


def place(rig, f, loc, rz=0, rx=0, ry=0):
    rig.location = loc; rig.rotation_euler = (rx, ry, rz)
    rig.keyframe_insert('location', frame=f); rig.keyframe_insert('rotation_euler', frame=f)


def blink(parts, frames):
    eyes = [o for o, b in parts if o.name.startswith('eye ') and 'shine' not in o.name]
    for o in eyes:
        z = o.scale.z
        for f in frames:
            for df, k in ((-3, 1), (0, .12), (3, 1)):
                o.scale.z = z * k; o.keyframe_insert('scale', frame=max(1, f + df), index=2)
        o.scale.z = z


def bunny(M, kind, loc=(0, 0, 0), rz=0, s=1.0, shirt='shirt_blue', tie=None, card=False, extra=None):
    """Rabbit plus accessories; accessories are skinned while the rig is still at the origin."""
    rig, parts = rabbit(kind, M, shirt, tie)
    if card:
        parts += [(o, 'body') for o in skin(lanyard(M, fool=(card == 'fool')), rig, 'body')]
    if extra:
        for fn, bone in extra:
            parts += [(o, bone) for o in skin(fn(M), rig, bone)]
    rig.location = loc; rig.rotation_euler.z = rz; rig.scale = (s, s, s)
    return rig, parts


def made(fn):
    """Objects created by fn()."""
    before = set(bpy.context.scene.objects)
    fn()
    return [o for o in bpy.context.scene.objects if o not in before]


def skin(objs, rig, bone):
    """Same rigid skinning as characters.rabbit: object parent + one full-weight group + Armature modifier."""
    out = []
    for o in objs:
        if o.type in ('CURVE', 'FONT'):
            bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active = o; o.select_set(True)
            bpy.ops.object.convert(target='MESH'); o = bpy.context.object; o.select_set(False)
        o.parent = rig; vg = o.vertex_groups.new(name=bone); vg.add(list(range(len(o.data.vertices))), 1, 'REPLACE')
        mod = o.modifiers.new('character skin', 'ARMATURE'); mod.object = rig
        out.append(o)
    return out


def headphones(M):
    def make():
        torus('headphone band', (0, .05, 2.65), .95, .07, M['phones'], rot=(pi / 2, 0, 0))
        for sx in (-1, 1):
            o = cylinder('headphone cup', (sx * .9, -.05, 2.5), .26, .2, M['phones']); o.rotation_euler.y = pi / 2
    return made(make)


def qsign(M):
    """A "?" paddle held in the right hand (rest pose), so a raised hand reads above the ears."""
    hand = Vector((-.92, -.08, 1.06)); d = Vector((-.45, -.05, -.72)).normalized()
    tip = hand + d * 1.0

    def make():
        rod('question stick', hand, tip, .04, M['wood'])
        o = cylinder('question disk', tip + d * .35, .42, .08, M['sticky_y']); o.rotation_euler.x = pi / 2
        for y, rz in ((-.06, 0), (.06, pi)):
            t = text('question mark', '¿', tip + d * .35 + Vector((0, y, 0)), .55, M['deadline'], (pi / 2, 0, rz))
    return made(make)


def laurel(M):
    return made(lambda: torus('laurel crown', (0, 0, 3.2), .66, .07, M['laurel']))


def lanyard(M, fool=False):
    """Neck strap + ID card on the chest (rig at the origin). The Fool's card shows the tarot art."""
    before = set(bpy.context.scene.objects)
    line('lanyard strap', [(-.30, -.36, 1.92), (-.16, -.52, 1.68), (0, -.56, 1.52), (.16, -.52, 1.68), (.30, -.36, 1.92)], .022,
         M['deadline'] if fool else M['marker_b'])
    cube('id card holder', (0, -.58, 1.30), (.36, .03, .50), M['white'], .02)
    if fool:
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -.598, 1.30), rotation=(pi / 2, 0, 0))
        o = bpy.context.object; o.name = 'fool id art'; o.scale = (.32, .46, 1)
        o.data.materials.append(image_mat('fool card art', P / 'assets/cards/the-fool.webp'))
    else:
        cube('id photo', (0, -.6, 1.40), (.18, .01, .18), M['sticky_b'], 0)
    return [o for o in bpy.context.scene.objects if o not in before]


def image_mat(name, path, glow=.15):
    m = bpy.data.materials.new(name); m.use_nodes = True; n = m.node_tree.nodes
    b = n.get('Principled BSDF'); tex = n.new('ShaderNodeTexImage'); tex.image = bpy.data.images.load(str(path), check_existing=True)
    m.node_tree.links.new(tex.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = .4
    m.node_tree.links.new(tex.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = glow
    return m


def text(name, body, loc, size, mat, rot=(pi / 2, 0, 0)):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.size = size; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    cu.extrude = size * .06
    o = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(o); o.location = loc; o.rotation_euler = rot
    o.data.materials.append(mat)
    return o


def holder(name, loc=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(o); o.location = loc
    if parent:
        o.parent = parent
    return o


def adopt(objs, root):
    for o in objs:
        if o.parent is None:
            o.parent = root
            o.matrix_parent_inverse = root.matrix_world.inverted()
    return root


def build_group(name, fn, loc=(0, 0, 0), rz=0):
    """Run fn() (which creates objects around the origin), parent the new top-level objects to one empty."""
    before = set(bpy.context.scene.objects)
    fn()
    root = holder(name)
    for o in bpy.context.scene.objects:
        if o not in before and o is not root and o.parent is None:
            o.parent = root
    root.location = loc; root.rotation_euler.z = rz
    return root


# ---------------------------------------------------------------- office props

def desk(M, monitor=True, screen='screen_dim', w=3.0, d=1.6, top=2.05):
    def make():
        cube('desk top', (0, 0, top), (w, d, .12), M['desk'], .04)
        for x in (-w / 2 + .15, w / 2 - .15):
            cube('desk leg', (x, 0, top / 2), (.12, d - .2, top - .1), M['desk_leg'], .03)
        if monitor:
            cube('monitor stand', (.35, -.45, top + .25), (.18, .14, .45), M['frame'], .03)
            cube('monitor frame', (.35, -.48, top + .95), (1.5, .10, .95), M['frame'], .05)
            cube('monitor screen', (.35, -.42, top + .95), (1.38, .02, .83), M[screen], 0)
            cube('keyboard', (.2, .15, top + .08), (.9, .3, .05), M['white'], .02)
            cube('folder stack', (-1.0, -.3, top + .15), (.5, .4, .18), M['folder_b'], .02)
    return make


def laptop(M, screen='screen'):
    """Open laptop, screen facing +Y (towards the user); the lid back faces -Y and carries stickers."""
    def make():
        cube('laptop base', (0, 0, .04), (1.25, .85, .07), M['frame'], .02)
        cube('laptop keys', (0, .05, .085), (1.05, .5, .01), M['chair_seat'], 0)
        lid = holder('laptop hinge', (0, -.42, .08))
        lid.rotation_euler.x = -.25
        for o in (cube('laptop lid', (0, 0, .45), (1.25, .05, .85), M['frame'], .02),
                  cube('laptop screen', (0, .03, .45), (1.12, .01, .74), M[screen], 0),
                  sticky(M, (-.3, -.035, .62), 'sticky_y', (0, 0, .2), .22), sticky(M, (.32, -.035, .3), 'sticky_b', (0, 0, -.15), .22)):
            o.parent = lid
    return make


def office_chair(M):
    def make():
        cylinder('chair seat', (0, 0, 1.0), .62, .16, M['chair_seat'])
        cube('chair back', (0, .55, 1.75), (1.05, .14, 1.1), M['chair_seat'], .12)
        rod('chair pole', (0, 0, .25), (0, 0, .95), .07, M['chair'])
        for k in range(5):
            a = k * 2 * pi / 5
            rod('chair foot', (0, 0, .22), (.6 * cos(a), .6 * sin(a), .14), .05, M['chair'])
            sphere('caster', (.6 * cos(a), .6 * sin(a), .09), (.09, .09, .09), M['chair'])
    return make


def cylinder(name, loc, r, depth, mat, verts=40):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc)
    o = bpy.context.object
    be = o.modifiers.new('soft edge', 'BEVEL'); be.width = min(r, depth) * .2; be.segments = 3
    return finish(o, name, mat)


def wall_clock(M, loc, rot=(pi / 2, 0, 0)):
    root = holder('wall clock', loc); root.rotation_euler = rot
    for o in (cylinder('clock rim', (0, 0, 0), .7, .16, M['clock_rim']), cylinder('clock face', (0, 0, .05), .6, .12, M['clock_face'])):
        o.parent = root
    hands = []
    for name, ln, wdt in (('hour hand', .32, .06), ('minute hand', .5, .04)):
        piv = holder(name + ' pivot', (0, 0, .13), root)
        c = cube(name, (0, ln / 2, 0), (wdt, ln, .03), M['hands'], 0); c.parent = piv
        hands.append(piv)
    return root, hands


def window(M, loc, w=3.2, h=3.6, sky='sky_morning'):
    def make():
        cube('window sky', (0, .05, 0), (w, .04, h), M[sky], 0)
        for x in (-w / 2, 0, w / 2):
            cube('window mullion', (x, 0, 0), (.12, .16, h + .12), M['white'], .02)
        for z in (-h / 2, h / 2):
            cube('window sill', (0, 0, z), (w + .12, .16, .12), M['white'], .02)
    return build_group('window', make, loc)


def plant(M, loc):
    def make():
        cylinder('plant pot', (0, 0, .4), .35, .8, M['pot'])
        for k in range(7):
            a = k * 2 * pi / 7
            sphere('leaf', (.25 * cos(a), .25 * sin(a), 1.1 + .15 * (k % 3)), (.16, .16, .42), M['plant']).rotation_euler = (.5 * sin(a), .5 * cos(a), 0)
    return build_group('plant', make, loc)


def sticky(M, loc, col='sticky_y', rot=(0, 0, 0), s=.32):
    o = cube('sticky note', loc, (s, .015, s), M[col], 0); o.rotation_euler = rot
    return o


def folder(M, loc, col='folder_b', rot=(0, 0, 0)):
    o = cube('folder', loc, (.7, .06, .9), M[col], .02); o.rotation_euler = rot
    return o


def office_room(M, size=(26, 30), wall_y=12, windows=True):
    """Floor, back wall, side wall with windows, ceiling lamps out of frame."""
    cube('ENV_floor', (0, 0, -.05), (size[0], size[1], .1), M['floor'], 0)
    cube('ENV_back_wall', (0, wall_y, 6), (size[0], .3, 12), M['wall'], 0)
    wins = []
    if windows:
        for x in (-6, 0, 6):
            wins.append(window(M, (x, wall_y - .2, 5.5)))
    return wins


def office_rows(M, rng, rows=3, xs=(-3.2, 3.2), y0=0, dy=-4.2, skip=(), workers=True, hunched=True, f_end=200):
    """Pairs of desks either side of an aisle along Y, with hunched worker rabbits facing +Y screens."""
    shirts = ['shirt_blue', 'shirt_pink', 'shirt_mint', 'shirt_yellow', 'shirt_lilac']
    rigs = []
    for i in range(rows):
        for x in xs:
            if (i, x) in skip:
                continue
            y = y0 + i * dy
            build_group('desk', desk(M), (x, y + 1.2, 0), pi)
            build_group('chair', office_chair(M), (x, y - .6, 0))
            if workers:
                r, parts = bunny(M, 'worker', (x, y - .6, .45), rz=pi, s=1.0, shirt=rng.choice(shirts), card='worker')
                pose(r, 1, SIT, body=(.35 if hunched else 0, 0, 0), head=(.25 if hunched else 0, 0, 0))
                rigs.append((r, parts))
    return rigs


# ---------------------------------------------------------------- the plush lion "งาน"

def lion(M, seed=3):
    """Giant plush lion facing -Y. Returns dict of control empties: root, body, head, jaw, tail, legs[4]."""
    rng = random.Random(seed)
    root = holder('LION_root')
    body = holder('LION_body', (0, 0, 2.3), root)
    head = holder('LION_head', (0, -2.4, 1.5), body)
    jaw = holder('LION_jaw', (0, -1.05, -.55), head)
    tail = holder('LION_tail', (0, 2.4, .4), body)

    def own(o, par):
        o.parent = par
        return o

    own(sphere('lion torso', (0, 0, 0), (1.55, 2.6, 1.35), M['lion'], seg=40, rings=28), body)
    own(sphere('lion belly', (0, -.4, -.45), (1.25, 1.9, .95), M['lion_belly']), body)
    own(sphere('lion head', (0, 0, 0), (1.35, 1.2, 1.25), M['lion'], seg=40, rings=28), head)
    own(sphere('lion muzzle', (0, -1.0, -.25), (.8, .5, .55), M['lion_belly']), head)
    own(sphere('lion nose', (0, -1.45, .02), (.28, .18, .2), M['lion_nose']), head)
    own(sphere('lion jaw', (0, -.1, 0), (.55, .32, .22), M['lion_nose']), jaw)
    own(sphere('lion chin', (0, -.15, -.18), (.6, .36, .2), M['lion_belly']), jaw)
    for sx in (-1, 1):
        own(sphere('lion eye', (sx * .55, -1.05, .45), (.17, .1, .2), M['eye']), head)
        own(sphere('lion eye shine', (sx * .55 - .05, -1.14, .52), (.05, .03, .06), M['white'], seg=16, rings=10), head)
        own(sphere('lion ear', (sx * 1.0, -.1, 1.0), (.35, .2, .35), M['lion']), head)
        own(sphere('lion brow', (sx * .55, -1.1, .78), (.24, .06, .07), M['lion_nose']), head)
    # Paper mane: documents and sticky notes fanned around the face.
    cols = ['paper', 'paper', 'paper', 'sticky_y', 'sticky_p', 'sticky_b']
    for ring, (r, n, sz) in enumerate(((1.45, 22, (.75, 1.0)), (1.85, 26, (.85, 1.15)))):
        for k in range(n):
            a = k * 2 * pi / n + ring * .12
            o = cube('mane sheet', (r * cos(a), .25 + ring * .25, r * sin(a)), (sz[0], .03, sz[1]), M[rng.choice(cols)], 0)
            # long edge (local Z) points radially out of the face plane (XZ)
            o.rotation_euler = (rng.uniform(-.3, .3), pi / 2 - a + rng.uniform(-.25, .25), 0)
            own(o, head)
    # Collar and DEADLINE tag
    o = torus('lion collar', (0, -2.0, .9), 1.05, .1, M['deadline'], rot=(pi / 2 - .5, 0, 0)); own(o, body)
    tag = holder('LION_tag', (0, -2.55, .25), body)
    own(cube('deadline tag', (0, 0, 0), (1.5, .08, .55), M['deadline'], .04), tag)
    own(text('deadline text', 'DEADLINE', (0, -.06, 0), .32, M['white']), tag)
    legs = []
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        hip = holder('LION_leg', (sx * .95, sy * 1.6, -.5), body)
        own(sphere('lion leg', (0, 0, -.7), (.5, .5, 1.0), M['lion']), hip)
        own(sphere('lion paw', (0, -.25, -1.55), (.6, .7, .38), M['lion_belly']), hip)
        legs.append(hip)
    seg = holder('LION_tail_tip', (0, .9, .9), tail)
    own(rod('lion tail', (0, 0, 0), (0, .9, .9), .14, M['lion']), tail)
    for k in range(5):
        own(cube('tail sticky', (.2 * cos(k), .1, .2 * sin(k)), (.38, .02, .38), M[cols[3 + k % 3]], 0), seg).rotation_euler = (k, k * .7, 0)
    return {'root': root, 'body': body, 'head': head, 'jaw': jaw, 'tail': tail, 'legs': legs, 'tag': tag}


def key_rot(o, f, rot):
    o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)


def key_loc(o, f, loc):
    o.location = loc; o.keyframe_insert('location', frame=f)


def lion_trot(L, f0, f1, path0, path1, rz=0, bounce=.25, rate=.55):
    """Root along a straight path with a body bounce and alternating legs."""
    for f in range(f0, f1 + 1, 2):
        u = (f - f0) / max(1, f1 - f0); t = (f - f0) / FPS
        p = Vector(path0).lerp(Vector(path1), u)
        key_loc(L['root'], f, p); key_rot(L['root'], f, (0, 0, rz))
        key_loc(L['body'], f, (0, 0, 2.3 + bounce * abs(sin(t * pi / rate))))
        for i, leg in enumerate(L['legs']):
            key_rot(leg, f, (.55 * sin(t * 2 * pi / rate / 1 + (i in (1, 2)) * pi), 0, 0))
        key_rot(L['tail'], f, (.2, 0, .5 * sin(t * 5)))


# ---------------------------------------------------------------- colosseum

def lathe(name, profile, mat, seg=72, arc=2 * pi, start=0):
    verts, faces = [], []
    n = len(profile)
    steps = seg if arc >= 2 * pi - 1e-6 else seg + 1
    for i in range(steps):
        a = start + arc * i / seg
        for r, z in profile:
            verts.append((r * cos(a), r * sin(a), z))
    for i in range(seg):
        i2 = (i + 1) % steps
        for j in range(n - 1):
            faces.append((i * n + j, i2 * n + j, i2 * n + j + 1, i * n + j + 1))
    o = mesh(name, verts, faces, mat)
    return o


def colosseum(M, r0=16, tiers=6, step=(2.2, 1.6), gate_angle=-pi / 2, open_front=True):
    """Stepped stands around a sand arena centred at the origin. Front (−Y) arc left open for the camera."""
    cylinder('ENV_sand', (0, 0, -.1), r0 + 1, .2, M['sand'], 96)
    prof = [(r0, 0), (r0, 2.2)]
    for k in range(tiers):
        r = r0 + k * step[0]; z = 2.2 + k * step[1]
        prof += [(r + step[0], z), (r + step[0], z + step[1])]
    gap = .62 if open_front else 0
    arc = 2 * pi - gap
    start = -pi / 2 + gap / 2
    st = lathe('ENV_stands', prof, M['stone'], 96, arc, start)
    st.data.materials.append(M['stone_dark'])
    for p in st.data.polygons:
        p.material_index = 1 if abs(p.normal.z) < .5 else 0
    for k in range(18):
        a = start + arc * (k + .5) / 18
        rr = r0 + tiers * step[0] + .2
        o = cube('banner', (rr * cos(a), rr * sin(a), 2.2 + tiers * step[1] + 1.6), (1.1, .1, 2.6), M['banner_red' if k % 2 else 'banner_purple'], .02)
        o.rotation_euler.z = a + pi / 2
    # arena wall ring and the gate
    wall = lathe('ENV_arena_wall', [(r0 - .05, 0), (r0 - .05, 2.3), (r0 + .3, 2.3)], M['stone_dark'], 96, arc, start)
    if open_front:
        for sx in (-1, 1):   # gate pillars either side of the opening
            a = -pi / 2 + sx * gap / 2
            cube('gate pillar', (r0 * cos(a), r0 * sin(a), 3.0), (1.0, 1.0, 6.0), M['stone_dark'], .06)
        cube('gate lintel', (0, -r0, 6.3), (r0 * gap + 1.4, 1.0, .9), M['stone_dark'], .06)
    return st


def noble(M, loc, rz, s=.8):
    return bunny(M, 'worker', loc, rz, s, shirt='toga', extra=[(laurel, 'head')])


def throne(M, loc, rz):
    def make():
        cube('throne seat', (0, 0, .9), (2.2, 1.8, .5), M['gold'], .08)
        cube('throne back', (0, .85, 2.6), (2.2, .3, 3.4), M['banner_purple'], .15)
        cube('throne back trim', (0, .7, 4.25), (2.4, .35, .3), M['gold'], .08)
        for x in (-1.15, 1.15):
            cube('throne arm', (x, -.1, 1.6), (.3, 1.6, .3), M['gold'], .08)
    return build_group('throne', make, loc, rz)


def grapes(M, loc):
    def make():
        for k in range(9):
            sphere('grape', (.12 * cos(k * 2.1), .12 * sin(k * 2.1), -.13 * (k // 3)), (.1, .1, .1), M['grape'], seg=16, rings=10)
    return build_group('grapes', make, loc)


# ---------------------------------------------------------------- the tower, the mug, the pile of work

def tower(M, loc=(0, 13, 0), h=9.2):
    """Office watchtower: a pale shaft with window bands and a railed balcony on top.
    The balcony floor sits at h + .6, which is where the senior rabbits stand."""
    def make():
        cube('tower shaft', (0, 0, h / 2), (5.0, 5.0, h), M['stone'], .10)
        cube('tower base', (0, 0, .35), (6.2, 6.2, .7), M['stone_dark'], .08)
        for k in range(3):
            cube('tower window', (0, -2.55, 2.4 + k * 2.3), (3.2, .22, .95), M['screen_dim'], .04)
        cube('tower balcony', (0, 0, h + .3), (7.4, 7.4, .6), M['stone_dark'], .08)
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):   # waist-high: hands and mugs stay visible
            cube('balcony post', (sx * 3.4, sy * 3.4, h + 1.05), (.3, .3, 1.3), M['stone_dark'], .04)
        for sy in (-1, 1):
            for z in (h + .75, h + 1.35):
                cube('balcony rail', (0, sy * 3.4, z), (7.2, .22, .22), M['stone_dark'], .06)
        for sx in (-1, 1):
            for z in (h + .75, h + 1.35):
                cube('balcony rail side', (sx * 3.4, 0, z), (.22, 7.2, .22), M['stone_dark'], .06)
    return build_group('tower', make, loc)


def mug(M, steam=True, col='clock_rim'):
    """A coffee mug around the origin, for riding on a holder that follows a hand."""
    def make():
        cylinder('mug body', (0, 0, 0), .26, .36, M[col])
        cylinder('mug coffee', (0, 0, .16), .225, .05, M['coffee'])
        torus('mug handle', (.3, 0, -.02), .13, .035, M[col], rot=(pi / 2, 0, 0))
        if steam:
            for k in range(3):
                sphere('mug steam', (.04 * cos(k * 2.2), .04 * sin(k * 2.2), .3 + .11 * k),
                       (.045 - .006 * k, .045 - .006 * k, .055), M['white'], seg=12, rings=8)
    return made(make)


def senior(M, loc, rz, s=.85, shirt='shirt_lilac'):
    """A senior rabbit: office shirt and tie, no laurel."""
    return bunny(M, 'worker', loc, rz, s, shirt=shirt, tie='navy')


def workpile(M, seed=4):
    """Giant mound of boxes, folders and paper facing -Y, roughly 3.5 x 4.8 x 4 units.
    Control empties: root (ground), body (the mound, z 2.2 above root), face (-Y front), tag.
    'toy' and 'eyes' are built at scale 0: a shot pops them in on the word ของเล่น."""
    rng = random.Random(seed)
    root = holder('PILE_root')
    body = holder('PILE_body', (0, 0, 2.2), root)
    face = holder('PILE_face', (0, -1.95, .5), body)
    tag = holder('PILE_tag', (0, -2.05, -1.0), body)

    def own(o, par):
        o.parent = par
        return o

    for k in range(30):                                        # the mound: boxes inside an ellipsoid
        a = rng.uniform(0, 2 * pi); r = rng.uniform(0, 1) ** .6
        x, y = 1.55 * r * cos(a), 2.15 * r * sin(a)
        z = (1 - r * r) * 2.0 - 1.5
        s = rng.uniform(.5, .95)
        o = cube('work box', (x, y, z), (s * 1.4, s * 1.1, s * .85), M['box' if k % 3 else 'box_dark'], .05)
        o.rotation_euler = (rng.uniform(-.12, .12), rng.uniform(-.12, .12), rng.uniform(-.6, .6))
        own(o, body)
    for k in range(20):                                        # folders and paper sticking out of it
        a = k * 2 * pi / 20 + .2
        o = cube('pile folder', (1.4 * cos(a), 1.9 * sin(a), rng.uniform(-.9, 1.4)), (.9, .06, 1.2),
                 M[rng.choice(['folder_b', 'folder_o', 'folder_g', 'paper', 'paper'])], .02)
        o.rotation_euler = (rng.uniform(-.35, .35), rng.uniform(-.5, .5), -a + rng.uniform(-.3, .3))
        own(o, body)
    for k in range(14):                                        # sticky notes all over it
        o = cube('pile sticky', (rng.uniform(-1.4, 1.4), rng.uniform(-1.9, 1.9), rng.uniform(.3, 2.0)),
                 (.34, .02, .34), M[rng.choice(['sticky_y', 'sticky_p', 'sticky_b'])], 0)
        o.rotation_euler = (rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))
        own(o, body)
    own(cube('deadline tag', (0, 0, 0), (1.5, .08, .55), M['deadline'], .04), tag)
    own(text('deadline text', 'DEADLINE', (0, -.06, 0), .32, M['white']), tag)
    toy = []                                                   # rocker rails and a handlebar
    for sx in (-1, 1):
        toy.append(own(rod('toy rail', (sx * 1.3, -2.5, -2.15), (sx * 1.3, 2.5, -2.15), .16, M['rail']), body))
        for sy in (-1, 1):
            toy.append(own(rod('toy rail curve', (sx * 1.3, sy * 2.5, -2.15), (sx * 1.3, sy * 3.1, -1.4), .16, M['rail']), body))
    toy.append(own(rod('toy handlebar', (-1.05, -1.95, 1.55), (1.05, -1.95, 1.55), .11, M['toy_bar']), body))
    for sx in (-1, 1):
        toy.append(own(rod('toy grip', (sx * 1.05, -1.95, 1.55), (sx * 1.3, -1.6, 1.55), .14, M['toy_bar']), body))
    eyes = []
    for sx in (-1, 1):
        eyes.append(own(sphere('pile eye white', (sx * .62, -.1, .55), (.32, .24, .32), M['white'], seg=20, rings=14), face))
        eyes.append(own(sphere('pile eye', (sx * .62, -.26, .5), (.16, .13, .16), M['eye'], seg=18, rings=12), face))
    for o in toy + eyes:
        o.scale = (0, 0, 0)
    return {'root': root, 'body': body, 'face': face, 'tag': tag, 'toy': toy, 'eyes': eyes}


def pop_in(objs, f, over=3):
    """Scale 0 -> 1 with a small overshoot, starting at frame f."""
    for o in objs:
        o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=f - 1)
        o.scale = (1.18,) * 3; o.keyframe_insert('scale', frame=f + over)
        o.scale = (1, 1, 1); o.keyframe_insert('scale', frame=f + over + 3)


def pile_lurch(PL, f0, f1, path0, path1, rate=.5, sway=.25):
    """The pile heaving along a path: the menacing version, for the chaos shot."""
    for f in range(f0, f1 + 1, 2):
        u = (f - f0) / max(1, f1 - f0); t = (f - f0) / FPS
        key_loc(PL['root'], f, Vector(path0).lerp(Vector(path1), u))
        key_rot(PL['root'], f, (0, 0, sway * sin(t * 2)))
        key_loc(PL['body'], f, (0, 0, 2.2 + .22 * abs(sin(t * pi / rate))))
        key_rot(PL['body'], f, (.12 * sin(t * 5), .1 * sin(t * 3.3), 0))


def pile_rock(PL, f0, f1, rate=.95, amp=.2):
    """The pile as a rocking toy: tips back and forth on its rails."""
    for f in range(f0, f1 + 1, 2):
        t = (f - f0) / FPS
        key_rot(PL['body'], f, (amp * sin(t * 2 * pi / rate), 0, 0))
        key_loc(PL['body'], f, (0, 0, 2.2 + .1 * abs(sin(t * 2 * pi / rate))))
