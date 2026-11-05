import bpy,sys,json,math,random
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(P/'blender'))
import fo_lib as L
FPS=30
SHOTS=json.loads((P/'timing/shots.json').read_text())

def clear():
 bpy.ops.wm.read_factory_settings(use_empty=True)

def character(fool=True,loc=(0,0,0),scale=4.15):
 if fool:
  with bpy.data.libraries.load(str(P/'assets/fool-expressions-approved.blend'),link=False) as (a,b):b.objects=[n for n in a.objects if n not in ('Key','Fill','Camera')]
  for o in b.objects:
   if o and o.name not in bpy.context.scene.objects:bpy.context.collection.objects.link(o)
  objs=[o for o in b.objects if o]
  if not any(o.type=='ARMATURE' for o in objs):raise RuntimeError('armature missing in approved library')
 else:
  before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(P/'assets/3d/glasses_rig.glb'));objs=[o for o in bpy.data.objects if o not in before]
 arm=next(o for o in objs if o.type=='ARMATURE');mesh=max((o for o in objs if o.type=='MESH'),key=lambda o:len(o.data.vertices));brows=[o for o in objs if o.name.startswith('Brow_')]
 for o in list(objs):
  if o.type=='MESH' and o is not mesh:bpy.data.objects.remove(o,do_unlink=True);objs.remove(o)
 # Snapshot the approved brow shapes; keep the approved morphs on the original mesh.
 poses={}
 if fool:
  for name,frame in [('neutral',1),('curious',32),('worried',55),('happy',84)]:
   bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();poses[name]=[[p.co.copy() for p in o.data.splines[0].points] for o in brows]
 for o in objs:
  o.animation_data_clear()
  if o.type=='CURVE':o.data.animation_data_clear()
 for pb in arm.pose.bones:pb.matrix_basis=Matrix.Identity(4)
 if mesh.data.shape_keys:
  mesh.data.shape_keys.animation_data_clear()
  for k in mesh.data.shape_keys.key_blocks:k.value=0
 root=bpy.data.objects.new('Fool_root' if fool else 'Scholar_root',None);bpy.context.collection.objects.link(root)
 for o in objs:
  if o.parent is None:o.parent=root
 for o in brows:o.matrix_basis=Matrix.Identity(4)
 root.scale=(scale,)*3;root.location=loc
 return {'root':root,'arm':arm,'mesh':mesh,'brows':brows,'poses':poses,'fool':fool,'base':Vector(loc)}

def mix(a,b,t):return a*(1-t)+b*t

def act(c,n,emotion='happy',mode='idle',start_emotion='neutral'):
 arm=c['arm'];head=arm.pose.bones.get('mixamorig:Head');rest=arm.matrix_local@arm.data.bones['mixamorig:Head'].matrix_local
 root=c['root'];base=c['base'];keys=c['mesh'].data.shape_keys
 for f in sorted(set(list(range(1,n+1,3))+[n])):
  u=(f-1)/max(n-1,1);t=(f-1)/FPS;e=min(1,max(0,(u-.12)/.35));e=e*e*(3-2*e)
  weights={name:(1-e if name==start_emotion else 0)+(e if name==emotion else 0) for name in ['neutral','curious','worried','happy']}
  happy=weights['happy'];weights['happy']*=.7;weights['neutral']+=happy*.3
  for pb in arm.pose.bones:pb.rotation_mode='QUATERNION';pb.rotation_quaternion=(1,0,0,0)
  def rot(name,axis,degrees):
   pb=arm.pose.bones.get('mixamorig:'+name)
   if not pb:return
   bpy.context.view_layer.update();pivot=(arm.matrix_local@pb.matrix).translation
   pb.matrix=arm.matrix_local.inverted()@Matrix.Translation(pivot)@Matrix.Rotation(math.radians(degrees),4,axis)@Matrix.Translation(-pivot)@arm.matrix_local@pb.matrix
  if mode=='walk':
   swing=math.sin(t*8);rot('LeftUpLeg','X',15*swing);rot('RightUpLeg','X',-15*swing);rot('LeftArm','X',-12*swing);rot('RightArm','X',12*swing)
   root.location=base+Vector((mix(-.65,.65,u),0,.055*abs(swing)))
  elif mode=='type':
   rot('LeftArm','X',-12+3*math.sin(t*14));rot('RightArm','X',-12-3*math.sin(t*14));rot('LeftForeArm','X',-12);rot('RightForeArm','X',-12)
  elif mode in ['ask','wave']:
   amount=min(1,u*4);rot('LeftArm','Y',(-42 if mode=='ask' else -70)*amount);rot('LeftArm','X',(-12 if mode=='ask' else -20)*amount);rot('LeftForeArm','Z',(7 if mode=='ask' else 15)*math.sin(t*8)*amount)
  elif mode=='offer':rot('LeftArm','X',-45*e);rot('RightArm','X',-45*e)
  else:rot('Spine1','X',2*math.sin(t*2))
  head.rotation_mode='XYZ';head.rotation_euler=(math.radians(5*weights['worried']-4*weights['happy']+1.5*math.sin(t*2)),math.radians(-10*weights['curious']+3*weights['worried']),math.radians(3*weights['curious']))
  for pb in arm.pose.bones:pb.keyframe_insert('rotation_euler' if pb==head else 'rotation_quaternion',frame=f)
  root.keyframe_insert('location',frame=f)
  if c['fool']:
   for name in ['curious','worried','happy']:keys.key_blocks[name].value=weights[name];keys.key_blocks[name].keyframe_insert('value',frame=f)
   blink=max(0,1-abs((t%2.6)-1.7)/.10);keys.key_blocks['blink'].value=blink*(1-.8*weights['happy']);keys.key_blocks['blink'].keyframe_insert('value',frame=f)
   bpy.context.view_layer.update();delta=arm.matrix_local@head.matrix@rest.inverted()
   for j,o in enumerate(c['brows']):
    for i,pt in enumerate(o.data.splines[0].points):
     pt.co=sum((c['poses'][name][j][i]*weights[name] for name in weights),Vector((0,0,0,0)));pt.keyframe_insert('co',frame=f)
    o.matrix_basis=delta;o.keyframe_insert('location',frame=f);o.keyframe_insert('rotation_euler',frame=f)

def prop(name,loc,height,rz=0):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(P/f'assets/3d/prop_{name}.glb'));objs=[o for o in bpy.data.objects if o not in before];bpy.context.view_layer.update()
 vs=[o.matrix_world@v.co for o in objs if o.type=='MESH' for v in o.data.vertices];mn=Vector([min(v[i] for v in vs) for i in range(3)]);mx=Vector([max(v[i] for v in vs) for i in range(3)]);s=height/(mx.z-mn.z);center=Vector(((mn.x+mx.x)/2,(mn.y+mx.y)/2,mn.z))
 root=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(root)
 for o in objs:
  if o.parent is None:
   mw=o.matrix_world.copy();o.parent=root;o.matrix_world=Matrix.Translation(-center)@mw
 root.scale=(s,)*3;root.location=loc;root.rotation_euler.z=rz
 return root

def setup(sid):
 clear();shot=SHOTS[sid-1];n=shot['frames'];sc=bpy.context.scene;sc.name=f'Fool_Work_{sid:02}'
 sc.render.engine='BLENDER_EEVEE';sc.eevee.taa_render_samples=16;sc.eevee.use_raytracing=False
 sc.render.resolution_x=1080;sc.render.resolution_y=1920;sc.render.resolution_percentage=100;sc.render.fps=FPS;sc.frame_start=1;sc.frame_end=n
 sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
 w=bpy.data.worlds.new('Pastel world');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.22,.16,.3,1);w.node_tree.nodes['Background'].inputs[1].default_value=.55;sc.world=w
 M=L.palette_fo();L.office_room(M,size=(20,26),wall_y=8,windows=True)
 L.plant(M,(-5,6,0));L.plant(M,(5,6,0));L.soft_rig((0,1,2),key=700,fill=450,sun=.8);L.light('Front softbox','AREA',(0,-6,7),(0,0,2),650,'FFF1E8',size=6)
 # Set dressing remains behind the actor, leaving the lower overlay safe area.
 for x in [-4,4]:prop('office-desk',(x,5,0),2.2,math.pi)
 target=(0,0,1.7);pos=(.6,-9,4);pos2=(.2,-8.5,3.8);lens=45
 if sid==1:
  f=character();act(f,n,'happy','idle','curious');pos=(0,-5.7,3.2);pos2=(.6,-8,3.7);target=(0,0,2.15)
 elif sid in [2,4]:
  f=character(loc=(0,0,0));act(f,n,'curious' if sid==4 else 'happy','type');prop('office-desk',(0,-1.45,0),2.4,math.pi)
  target=(0,0,2.2);pos=(3,-8,4);pos2=(2.1,-7.6,3.6)
 elif sid==3:
  f=character(loc=(-.8,0,0));act(f,n,'happy','offer','curious');toy=prop('paper-toy',(1.4,-.3,1.9),1.3)
  for frame,x,z in [(1,1.4,1.9),(n,2.1,2.7)]:toy.location.x=x;toy.location.z=z;toy.rotation_euler.z=frame/n*.8;toy.keyframe_insert('location',frame=frame);toy.keyframe_insert('rotation_euler',frame=frame)
  pos=(-1,-9,3.8);pos2=(1,-9,3.7)
 elif sid==5:
  prop('ivory-tower',(0,1,0),4.5);c=character(False,loc=(0,1,3.9),scale=2.5);act(c,n,'neutral')
  cup=prop('coffee-cup',(0,0,0),.42)
  for frame in list(range(1,n+1,3))+[n]:
   sc.frame_set(frame);bpy.context.view_layer.update();hand=c['arm'].pose.bones['mixamorig:RightHand'];cup.location=c['arm'].matrix_world@hand.tail+Vector((0,-.12,.02));cup.keyframe_insert('location',frame=frame)
  pos=(3,-13,7.0);pos2=(2,-12,6.0);target=(0,1,3.5);lens=42
 elif sid==6:
  f=character(loc=(-1.5,0,0));act(f,n,'worried','offer');pile=prop('work-pile',(1.6,0,0),4.5)
  for frame,rz in [(1,-.04),(n//2,.05),(n,-.04)]:pile.rotation_euler.y=rz;pile.keyframe_insert('rotation_euler',frame=frame)
  pos=(-2,-10,4.5);pos2=(0,-9.5,4);target=(0,0,1.8);lens=40
 elif sid==7:
  f=character(loc=(-1,0,0));act(f,n,'happy','walk','worried');pile=prop('work-pile',(2,1,0),3.4)
  toy=prop('paper-toy',(2,1,0),2.6)
  for o,show_first in [(pile,True),(toy,False)]:
   for frame,hide in [(1,not show_first),(int(n*.6),not show_first),(int(n*.6)+1,show_first),(n,show_first)]:
    for child in o.children_recursive:child.hide_render=hide;child.keyframe_insert('hide_render',frame=frame)
  pos=(-1,-10,4);pos2=(1,-9,3.8);lens=40
 elif sid==8:
  f=character(loc=(-.8,0,0));act(f,n,'happy','offer');toy=prop('paper-toy',(1.7,-.3,.8),2)
  for frame,z,ry in [(1,.8,-.2),(n//3,1.3,.2),(2*n//3,.65,-.1),(n,.8,0)]:toy.location.z=z;toy.rotation_euler.y=ry;toy.keyframe_insert('location',frame=frame);toy.keyframe_insert('rotation_euler',frame=frame)
  pos=(2,-9,3.8);pos2=(.8,-8.2,3.5);target=(0,0,1.9)
 elif sid==9:
  f=character(loc=(-1.2,0,0));act(f,n,'happy','wave');c=character(False,loc=(2.1,1.5,0),scale=3.7);act(c,n,'neutral');prop('work-pile',(3.5,3,0),2.3)
  pos=(-1,-9,3.7);pos2=(-.5,-8,3.6);target=(0,0,1.9)
 elif sid in [10,11]:
  f=character(loc=(0,-.4,0));act(f,n,'curious' if sid==10 else 'happy','idle' if sid==10 else 'ask','neutral' if sid==10 else 'curious')
  c=character(False,loc=(3,2.5,0),scale=3.6);act(c,n,'neutral');prop('office-desk',(2,1.5,0),1.4,math.pi)
  pos=(.6,-6.6,3.3);pos2=(.2,-6.3,3.2);target=(0,-.4,2.25);lens=46
 else:
  f=character(loc=(-1,0,0));act(f,n,'happy','wave');c=character(False,loc=(1.8,.5,0),scale=3.8);act(c,n,'neutral','wave');pos=(0,-9.5,3.8);pos2=(0,-10.3,4);target=(.2,0,1.8);lens=42
 cam,tgt=L.camera(sc,lens,5.6);cam.data.dof.use_dof=False
 L.cam_key(cam,tgt,1,pos,target);L.cam_key(cam,tgt,n,pos2,target)
 sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=94
 sc.frame_set(1);(P/'blender/scenes').mkdir(exist_ok=True)
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(P/f'blender/scenes/shot-{sid:02}.blend'),compress=True)
 return sc,n

if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:];sid=int(args[0]);sc,n=setup(sid)
 if '--render' in args:
  d=P/f'renders/shot-{sid:02}';d.mkdir(exist_ok=True);sc.render.filepath=str(d/'frame-');bpy.ops.render.render(animation=True)
 else:
  sc.frame_set(max(1,n//2));sc.render.filepath=str(P/f'review/shot-{sid:02}.jpg');bpy.ops.render.render(write_still=True)
