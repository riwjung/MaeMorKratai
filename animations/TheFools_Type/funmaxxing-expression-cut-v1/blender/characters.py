"""Original rigged MaeMorKratai rabbits and props, modeled in Blender from the approved A-pose references.

Copied from ep02-extra-funmaxxing-3d-v1/blender/characters.py; this copy adds the office worker
bunny (kind='worker', pastel shirt + optional tie) for The Fool at work."""
import bpy, math, random
from mathutils import Vector
from math import sin,cos,pi

def linear(h):
 h=h.lstrip('#'); vals=[int(h[i:i+2],16)/255 for i in (0,2,4)]
 return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals)

def material(name,h,rough=.55,metal=0,glow=0,noise=0):
 m=bpy.data.materials.new(name);m.use_nodes=True
 b=m.node_tree.nodes.get('Principled BSDF');c=linear(h)
 b.inputs['Base Color'].default_value=(*c,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
 if glow:b.inputs['Emission Color'].default_value=(*c,1);b.inputs['Emission Strength'].default_value=glow
 if noise:
  n=m.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=150;n.inputs['Detail'].default_value=2
  bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=noise
  m.node_tree.links.new(n.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],b.inputs['Normal'])
 return m

def palette():
 return {k:material(k,*args) for k,args in {
 'cream':('FFF5E5',.7,0,0,.012),'pink':('F1BBBD',.7),'eye':('49372F',.26),
 'nose':('FA6A54',.18),'white':('FFFDF7',.43),'peach':('ECA77C',.67,0,0,.008),'sage':('779F81',.65,0,0,.008),
 'navy':('3D4D69',.72,0,0,.008),'tunic':('B6A7C5',.75),'gold':('D9AC65',.32,.65),
 'wood':('8D6950',.65),'pages':('E6D5AF',.7),'purple':('57406D',.64),'lavender':('9477B4',.5),
 'ground':('342344',.7),'glow':('F9D999',.3,.1,3),'blue':('A8D9E6',.4,0,2),
 'red':('BC6675',.65),'teal':('5A8A92',.6)}.items()}

def finish(o,name,mat,parts=None,bone=None):
 o.name=name
 if mat:o.data.materials.append(mat)
 if o.type=='MESH':
  for p in o.data.polygons:p.use_smooth=True
 if parts is not None:parts.append((o,bone or 'body'))
 return o

def sphere(name,loc,scale,mat,parts=None,bone=None,seg=32,rings=20):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=loc);o=bpy.context.object;o.scale=scale
 return finish(o,name,mat,parts,bone)

def cube(name,loc,scale,mat,bevel=.05,parts=None,bone=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=scale
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('soft corners','BEVEL');mod.width=bevel;mod.segments=3
 o.modifiers.new('weighted normals','WEIGHTED_NORMAL')
 return finish(o,name,mat,parts,bone)

def rod(name,a,b,r,mat,parts=None,bone=None):
 v=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=r,depth=v.length,location=(Vector(a)+Vector(b))*.5)
 o=bpy.context.object;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();be=o.modifiers.new('rounded ends','BEVEL');be.width=r*.35;be.segments=3
 return finish(o,name,mat,parts,bone)

def line(name,pts,r,mat,parts=None,bone=None,closed=False):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=r;cu.bevel_resolution=3
 sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
 for p,co in zip(sp.bezier_points,pts):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 sp.use_cyclic_u=closed;o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o)
 return finish(o,name,mat,parts,bone)

def mesh(name,verts,faces,mat,parts=None,bone=None,sub=0):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
 if sub:mo=o.modifiers.new('smooth sculpt','SUBSURF');mo.levels=sub;mo.render_levels=sub
 return finish(o,name,mat,parts,bone)

def torus(name,loc,major,minor,mat,parts=None,bone=None,rot=(0,0,0)):
 bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=12,location=loc,major_radius=major,minor_radius=minor,rotation=rot)
 return finish(bpy.context.object,name,mat,parts,bone)

def sculpt_head(M,parts):
 o=sphere('soft sculpted cheeks',(0,0,2.62),(1,1,1),M['cream'],parts,'head',48,32)
 # A broad low cheek and narrower forehead keep the reference silhouette.
 for v in o.data.vertices:
  x,y,z=v.co;w=1.00+.16*math.exp(-((z+.35)/.43)**2)-.08*max(z,0)
  v.co=(x*w*.86,y*.65,z*.75)
 return o

def cloth_tail(name,M,parts):
 verts=[];faces=[]
 for j in range(9):
  t=j/8
  for i in range(5):
   u=i/4-.5;verts.append((.58+.53*t+.34*u,(.16+.18*sin(t*pi))+.05*cos(u*pi*4),1.95-.83*t+.10*u))
 for j in range(8):
  for i in range(4):a=j*5+i;faces.append((a,a+1,a+6,a+5))
 o=mesh(name,verts,faces,M['peach'],parts,'body',2);o.data.materials.append(M['sage'])
 for p in o.data.polygons:p.material_index=1 if (p.index//4)//2%2 else 0
 so=o.modifiers.new('scarf thickness','SOLIDIFY');so.thickness=.045
 return o

def cape(M,parts):
 verts=[];faces=[];n=40;m=10
 for j in range(m+1):
  t=j/m;r=.55+.38*t
  for i in range(n+1):
   a=-pi*.20+(pi*1.40)*i/n
   # open at the front (-Y), wrapped around shoulders and back.
   x=r*cos(a);y=r*sin(a);z=1.97-1.26*t+.06*cos(a*7)*t
   verts.append((x,y,z))
 for j in range(m):
  for i in range(n):k=j*(n+1)+i;faces.append((k,k+1,k+n+2,k+n+1))
 o=mesh('scholar cape',verts,faces,M['navy'],parts,'body',1);sol=o.modifiers.new('lined cape','SOLIDIFY');sol.thickness=.045
 edges=[verts[:n+1],verts[-n-1:],[verts[j*(n+1)] for j in range(m+1)],[verts[j*(n+1)+n] for j in range(m+1)]]
 for i,pts in enumerate(edges):line('cape gold piping '+str(i),pts,.023,M['gold'],parts,'body')
 sphere('lavender tunic',(0,0,1.15),(.70,.55,.77),M['tunic'],parts,'body')
 # Front clasp is a crescent-shaped solid curve in front of collar.
 crescent('moon clasp',(.0,-.64,1.95),.14,M['gold'],parts,'body')
 for x in [-.20,.20]:sphere('clasp button',(x,-.60,1.96),(.06,.04,.06),M['gold'],parts,'body')

def crescent(name,loc,r,mat,parts=None,bone=None):
 pts=[]
 for i in range(33):
  a=pi*.28+(pi*1.44)*i/32;pts.append((loc[0]+r*cos(a),loc[1],loc[2]+r*sin(a)))
 for i in range(33):
  t=i/32;z=-r*sin(pi*.28)+2*r*sin(pi*.28)*t
  x=loc[0]+r*.4-math.sqrt(max(0,(r*.85)**2-z*z))
  pts.append((x,loc[1],loc[2]+z))
 # Filled flat polygon, with depth bevel.
 o=mesh(name,pts,[tuple(range(len(pts)))],mat,parts,bone)
 so=o.modifiers.new('metal depth','SOLIDIFY');so.thickness=r*.16
 be=o.modifiers.new('metal bevel','BEVEL');be.width=r*.05;be.segments=2
 return o

def rabbit(kind,M,shirt='shirt_blue',tie=None):
 parts=[]
 sphere('pear body',(0,.035,1.18),(.66,.51,.86),M['cream'],parts,'body',40,28)
 sculpt_head(M,parts)
 for sign in [-1,1]:
  side='L' if sign==1 else 'R'
  e=sphere('ear '+side,(sign*.37,.035,3.55),(.265,.20,.71),M['cream'],parts,'ear.'+side);e.rotation_euler.y=sign*.13
  e=sphere('pink inner ear '+side,(sign*.38,-.158,3.56),(.145,.048,.49),M['pink'],parts,'ear.'+side);e.rotation_euler.y=sign*.13
  sphere('arm '+side,(sign*.67,-.015,1.45),(.245,.25,.48),M['cream'],parts,'arm.'+side).rotation_euler.y=-sign*.55
  sphere('pink palm '+side,(sign*.88,-.10,1.12),(.145,.16,.12),M['pink'],parts,'arm.'+side)
  sphere('leg '+side,(sign*.34,.0,.43),(.26,.32,.39),M['cream'],parts,'leg.'+side)
  sphere('foot '+side,(sign*.34,-.17,.24),(.33,.43,.23),M['cream'],parts,'leg.'+side)
  sphere('pink toes '+side,(sign*.34,-.528,.24),(.19,.047,.12),M['pink'],parts,'leg.'+side)
  sphere('eye '+side,(sign*.30,-.606,2.64),(.085,.056,.115),M['eye'],parts,'head')
  sphere('eye shine '+side,(sign*.30-.02,-.653,2.69),(.021,.012,.026),M['white'],parts,'head',20,12)
  sphere('cheek blush '+side,(sign*.51,-.563,2.39),(.14,.022,.058),M['pink'],parts,'head')
 sphere('round coral nose',(0,-.702,2.49),(.17,.135,.145),M['nose'],parts,'head')
 sphere('nose highlight',(-.052,-.816,2.547),(.049,.017,.034),M['white'],parts,'head',20,12)
 line('mouth left',[(-.22,-.658,2.31),(-.14,-.702,2.27),(-.06,-.724,2.30),(0,-.738,2.39)],.024,M['eye'],parts,'head')
 line('mouth right',[(0,-.738,2.39),(.06,-.724,2.30),(.14,-.702,2.27),(.22,-.658,2.31)],.024,M['eye'],parts,'head')
 sphere('round tail',(0,.53,.92),(.27,.27,.27),M['cream'],parts,'body')
 if kind=='traveler':
  o=torus('striped scarf collar',(0,0,1.95),.53,.16,M['peach'],parts,'body');o.scale=(1,.86,1)
  o.data.materials.append(M['sage'])
  for p in o.data.polygons:
   x,y,z=p.center;a=math.atan2(y,x);p.material_index=int((a+pi)*8/(2*pi))%2
  # polygon centers need an update before material assignment
  o.data.update()
  for p in o.data.polygons:p.material_index=int((math.atan2(p.center.y,p.center.x)+pi)*8/(2*pi))%2
  cloth_tail('trailing striped scarf',M,parts)
  sphere('scarf pin',(.54,-.19,1.97),(.07,.055,.07),M['gold'],parts,'body')
 elif kind=='worker':
  sphere('office shirt',(0,.02,1.22),(.70,.55,.80),M[shirt],parts,'body',40,28)
  for sign in [-1,1]:
   o=cube('shirt collar',(sign*.13,-.47,1.93),(.24,.05,.14),M['white'],.03,parts,'body');o.rotation_euler=(.35,0,sign*.5)
  if tie:cube('office tie',(0,-.55,1.62),(.13,.04,.50),M[tie],.03,parts,'body').rotation_euler.x=-.18
 else:
  cape(M,parts)
  for sign in [-1,1]:
   torus('brass spectacles',(sign*.30,-.714,2.63),.205,.020,M['gold'],parts,'head',(pi/2,0,0))
   line('glasses temple',[(sign*.50,-.70,2.66),(sign*.73,-.47,2.69),(sign*.73,-.20,2.68)],.019,M['gold'],parts,'head')
   line('worried eyebrow',[(sign*.19,-.60,2.98),(sign*.28,-.59,2.94),(sign*.37,-.55,2.93)],.025,M['eye'],parts,'head')
  line('spectacle bridge',[(-.10,-.756,2.65),(0,-.79,2.70),(.10,-.756,2.65)],.018,M['gold'],parts,'head')
 # True armature with rigid skin weights per sculpted part: no welded props.
 arm=bpy.data.armatures.new(kind+' skeleton');rig=bpy.data.objects.new(kind+' rig',arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True)
 bpy.ops.object.mode_set(mode='EDIT')
 specs={'root':((0,0,0),(0,0,.3),None),'body':((0,0,.8),(0,0,1.95),'root'),'head':((0,0,1.95),(0,0,2.9),'body')}
 for side,sgn in [('L',1),('R',-1)]:
  specs['ear.'+side]=((sgn*.3,0,3.0),(sgn*.42,0,4.15),'head')
  specs['arm.'+side]=((sgn*.47,0,1.8),(sgn*.92,-.05,1.08),'body')
  specs['leg.'+side]=((sgn*.32,0,.72),(sgn*.34,-.10,.20),'root')
 for name,(h,t,par) in specs.items():
  b=arm.edit_bones.new(name);b.head=h;b.tail=t
  if par:b.parent=arm.edit_bones[par]
 bpy.ops.object.mode_set(mode='OBJECT');bpy.ops.object.select_all(action='DESELECT')
 for o,bone in parts:
  if o.type=='CURVE':
   bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.select_set(False)
  o.parent=rig;vg=o.vertex_groups.new(name=bone);vg.add(list(range(len(o.data.vertices))),1,'REPLACE');mod=o.modifiers.new('character skin','ARMATURE');mod.object=rig
 for b in rig.pose.bones:b.rotation_mode='XYZ'
 return rig,parts

def group(name):
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);return o

def parent_group(objects,root):
 for o in objects:o.parent=root
 return root

def bindle(M,loc=(0,0,0)):
 before=set(bpy.context.scene.objects)
 rod('walking staff',(-.15,0,-.45),(.25,0,1.20),.045,M['wood'])
 o=sphere('orange cloth bundle',(-.29,.02,.75),(.33,.25,.31),M['peach'],seg=40,rings=24)
 for v in o.data.vertices:
  a=math.atan2(v.co.y,v.co.x);v.co.x*=1+.04*cos(a*9);v.co.y*=1+.04*cos(a*9)
 sphere('bundle knot',(-.26,0,1.05),(.09,.10,.10),M['peach'])
 for s in [-1,1]:sphere('cloth knot loop',(-.26+s*.10,0,1.15),(.12,.045,.08),M['peach']).rotation_euler.y=s*.5
 root=group('traveler bindle');parent_group([o for o in bpy.context.scene.objects if o not in before and o!=root],root);root.location=loc;return root

def flower(M,loc=(0,0,0)):
 before=set(bpy.context.scene.objects)
 line('daisy stem',[(0,0,0),(.025,0,.23),(0,0,.48)],.018,M['sage'])
 for k in range(8):
  a=k*pi/4;o=sphere('daisy petal',(.11*cos(a),-.015,.5+.11*sin(a)),(.07,.027,.12),M['white'],seg=20,rings=12);o.rotation_euler.y=pi/2-a
 sphere('daisy gold heart',(0,-.045,.5),(.072,.04,.072),M['gold'],seg=20,rings=12)
 root=group('white daisy');parent_group([o for o in bpy.context.scene.objects if o not in before and o!=root],root);root.location=loc;return root

def books(M,loc=(0,0,0)):
 before=set(bpy.context.scene.objects)
 for i in range(4):
  z=i*.25;w=1.06-.05*i;col=M[['purple','teal','navy','red'][i]]
  cube('book pages',(0,0,z+.13),(w-.07,.59,.17),M['pages'],.025)
  for dz in [.025,.235]:cube('book cover',(0,0,z+dz),(w,.65,.055),col,.025)
  cube('book spine',(-w/2+.03,0,z+.13),(.075,.65,.20),col,.025)
  for y in [-.24,.24]:cube('gold spine band',(-w/2-.01,y,z+.13),(.016,.045,.18),M['gold'],.008)
  for dz in [.09,.13,.17]:line('page edge',[(-w*.42,-.301,z+dz),(w*.43,-.301,z+dz)],.004,M['wood'])
 for k in range(3):
  x=(k-1)*.28
  rod('rolled map',(x,-.25,1.04),(x,.35,1.04),.105,M['pages'])
  for y in [-.26,.36]:torus('scroll spiral',(x,y,1.04),.071,.011,M['wood'],rot=(pi/2,0,0))
  rod('map red ribbon',(x,-.025,1.04),(x,.055,1.04),.111,M['red'])
 root=group('heavy scroll pile');parent_group([o for o in bpy.context.scene.objects if o not in before and o!=root],root);root.location=loc;return root

def stone(M,loc=(0,0,0),radius=.8,seed=0):
 rng=random.Random(seed);before=set(bpy.context.scene.objects);n=9;rs=[radius*rng.uniform(.85,1.1) for _ in range(n)];verts=[]
 for z,f in [(0,1),(-.12,1.05),(-.45,.75),(-.85,.18)]:
  for k,r in enumerate(rs):a=k*2*pi/n;verts.append((r*f*cos(a),r*f*sin(a),z))
 faces=[tuple(range(n))]
 for j in range(3):
  for k in range(n):a=j*n+k;b=j*n+(k+1)%n;faces.append((a,b,b+n,a+n))
 faces.append(tuple(range(3*n,4*n)))
 o=mesh('floating purple stone',verts,faces,M['purple']);o.data.materials.append(M['lavender']);o.data.polygons[0].material_index=1
 be=o.modifiers.new('worn edges','BEVEL');be.width=.06;be.segments=3;o.modifiers.new('stone normals','WEIGHTED_NORMAL')
 pts=[(r*cos(k*2*pi/n),r*sin(k*2*pi/n),-.055) for k,r in enumerate(rs)];line('gold stone rim',pts,.018,M['gold'],closed=True)
 root=group('stepping stone');parent_group([o for o in bpy.context.scene.objects if o not in before and o!=root],root);root.location=loc;return root

def attach(root,rig,bone,loc):
 # Bone parent placed in the desired local rest-space coordinates.
 root.parent=rig;root.parent_type='BONE';root.parent_bone=bone
 bpy.context.view_layer.update();root.matrix_parent_inverse=(rig.matrix_world@rig.pose.bones[bone].matrix).inverted()
 root.location=loc
