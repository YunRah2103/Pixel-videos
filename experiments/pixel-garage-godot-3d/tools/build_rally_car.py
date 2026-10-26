#!/usr/bin/env python3
"""Original full-surface Blender automotive modelling for the Pixel Garage Godot film.
No asset downloads: sectional hatchback, boolean-cut wheel arches and editable assemblies.
Godot car forward points along -Z; metres and Y-up.
"""
import bpy, math, os
from mathutils import Vector
from math import sin, cos, pi

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,"assets","rally_car_body.glb")
os.makedirs(os.path.dirname(OUT),exist_ok=True)

def paint(name,color,metal=0.0,rough=.65):
    m=bpy.data.materials.new(name)
    m.diffuse_color=tuple(color)+(1.0,)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Base Color"].default_value=tuple(color)+(1.0,)
        bs.inputs["Metallic"].default_value=metal
        bs.inputs["Roughness"].default_value=rough
    return m

cream=paint("01_OysterCreamMotorsport",(.72,.71,.64),.13,.53)
light=paint("02_AluminiumWarm",(.51,.60,.59),.21,.54)
black=paint("03_CarbonCharcoal",(.042,.070,.072),.09,.82)
glass=paint("04_TealGlass",(.067,.15,.19),.08,.23)
reflection=paint("05_GlassPixelReflection",(.21,.43,.46),.10,.28)
aqua=paint("06_TealRallyStripe",(.018,.57,.52),.14,.49)
orange=paint("07_OrangeRallyStripe",(.90,.26,.10),.05,.61)
lamps=paint("08_LED_Headlamps",(.72,.86,.73),.0,.24)
taillight=paint("09_RearLamps",(.87,.12,.07),.0,.25)
gold=paint("10_HoodNumberGold",(.92,.68,.32),.0,.48)

def object_mesh(name,points,faces,material,bevel=0.0):
    m=bpy.data.meshes.new(name+"Mesh")
    m.from_pydata(points,[],faces)
    m.update()
    obj=bpy.data.objects.new(name,m)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    if bevel>0:
        mod=obj.modifiers.new("soft precision edges","BEVEL")
        mod.width=bevel
        mod.segments=2
        mod.affect="EDGES"
        mod.limit_method="ANGLE"
        mod.angle_limit=.6
        bpy.context.view_layer.objects.active=obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    for p in obj.data.polygons: p.use_smooth=True
    return obj

def panel(name,pts,material,bevel=0):
    verts=[tuple(v) for v in pts]
    return object_mesh(name,verts,[tuple(range(len(verts)))],material,bevel)

def rounded_box(name,xyz,size,material,radius=.035):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz)
    obj=bpy.context.object
    obj.name=name
    obj.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    obj.data.materials.append(material)
    if radius:
        mod=obj.modifiers.new("Hand-bevel","BEVEL")
        mod.width=radius
        mod.segments=2
        bpy.ops.object.modifier_apply(modifier=mod.name)
        mod=obj.modifiers.new("Weighted vertex normals","WEIGHTED_NORMAL")
    return obj

def tube(name,a,b,r,material,vertices=9):
    a,b=Vector(a),Vector(b)
    d=b-a
    mid=(a+b)*.5
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=r, depth=d.length, location=mid)
    ob=bpy.context.object
    ob.name=name
    ob.rotation_euler=d.to_track_quat("Z","Y").to_euler()
    ob.data.materials.append(material)
    return ob

def interp(x,samples):
    samples=sorted(samples)
    for (a,va),(b,vb) in zip(samples,samples[1:]):
        if a<=x<=b: return va+(vb-va)*(x-a)/(b-a)
    return samples[0][1] if x<samples[0][0] else samples[-1][1]

BODY_Z=[-2.20,-2.05,-1.72,-1.3,-.85,-.35,.25,.9,1.3,1.72,2.11]
W=[.55,.77,.86,.92,.92,.93,.92,.90,.88,.83,.65]
H=[.67,.78,.89,.94,.99,1.01,1.03,1.03,1.01,.94,.75]
zs=[-2.20+i*(4.31/48) for i in range(49)]
n=14
verts=[]
for z in zs:
    w=interp(z,list(zip(BODY_Z,W)))
    h=interp(z,list(zip(BODY_Z,H)))
    contour=[(-.77,.31),(-.97,.36),(-1.02,.54),(-1.00,h-.17),(-.91,h-.035),(-.68,h+.018),(0,h+.026),(.68,h+.018),(.91,h-.035),(1.00,h-.17),(1.02,.54),(.97,.36),(.77,.31),(0,.30)]
    for x,y in contour:
        verts.append((x*w,y,z))
faces=[]
for i in range(len(zs)-1):
    for j in range(n):
        a=i*n+j;b=i*n+(j+1)%n;c=(i+1)*n+(j+1)%n;d=(i+1)*n+j
        faces.append((a,b,c,d))
# Solid end caps for real wheel-arch booleans.
faces.append(tuple(reversed(range(n))))
faces.append(tuple((len(zs)-1)*n+i for i in range(n)))
body=object_mesh("01_ContinuousRoundedShell_WithTrueWheelArchCutouts",verts,faces,cream)
for z in [-1.26,1.24]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.436,depth=3.8,location=(0,.38,z),rotation=(0,pi/2,0))
    cutter=bpy.context.object
    cutter.name="temporary_boolean_arch"
    bpy.context.view_layer.objects.active=body
    mod=body.modifiers.new("RealWheelArch", "BOOLEAN")
    mod.operation="DIFFERENCE"
    mod.solver="EXACT"
    mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
# Slightly reflective hand-designed fender bulges.
for side in [-1,1]:
    for z in [-1.26,1.24]:
        bpy.ops.mesh.primitive_torus_add(major_segments=36,minor_segments=7,location=(side*.914,.38,z),rotation=(0,pi/2,0),major_radius=.435,minor_radius=.038)
        ob=bpy.context.object
        ob.name="02_ArchedFenderProfile"
        ob.data.materials.append(light)

# Greenhouse cross-section: raked windshield, short roof, upright rear hatch.
cabins=[(-.97,.81,1.00,1.045),(-.15,.655,1.03,1.565),(1.03,.67,1.03,1.555),(1.66,.78,1.01,1.07)]
upper=[]
for z,w,base,top in cabins:
    upper.extend([(-w,base,z),(w,base,z),(w,top,z),(-w,top,z)])
cfaces=[]
for i in range(3):
    for j in range(4):
        cfaces.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
cfaces.extend([(3,2,1,0),(12,13,14,15)])
object_mesh("03_FiveDoorHatchbackCabinStructuralVolume",upper,cfaces,black,.014)
# Real physical glazing offset from cabin frame.
panel("04_RakedWindshield",[
(-.759,1.066,-.969),(.759,1.066,-.969),(.616,1.52,-.173),(-.616,1.52,-.173)],glass)
panel("05_RearWindow",[
(-.625,1.504,1.06),(.625,1.504,1.06),(.733,1.085,1.676),(-.733,1.085,1.676)],glass)
panel("06_CrownedRoof",[
(-.64,1.578,-.16),(.64,1.578,-.16),(.654,1.572,1.04),(-.654,1.572,1.04)],cream)
for side in [-1,1]:
    S=lambda p:(side*p[0],p[1],p[2])
    panel("07_FrontDoorGlassLeftRight",[S((.773,1.057,-.81)),S((.636,1.513,-.125)),S((.645,1.515,.28)),S((.789,1.060,.26))],glass)
    panel("08_RearDoorGlassLeftRight",[S((.789,1.060,.32)),S((.65,1.515,.34)),S((.652,1.511,1.00)),S((.762,1.068,1.51))],glass)
    panel("09_AngledWindshieldHighlight",[S((.755,1.07,-.78)),S((.643,1.462,-.13)),S((.648,1.462,-.02)),S((.764,1.07,-.61))],reflection)
    tube("10_Bpillar",S((.796,1.06,.29)),S((.661,1.557,.29)),.027,cream)
    tube("11_Apillar",S((.83,1.02,-.97)),S((.66,1.575,-.16)),.031,cream)
    tube("12_Cpillar",S((.669,1.561,1.04)),S((.81,1.02,1.68)),.047,cream)
    tube("13_RoofRail",S((.66,1.586,-.13)),S((.67,1.586,1.03)),.027,light)
    tube("14_WindowSill",S((.79,1.064,-.80)),S((.79,1.063,1.50)),.019,light)
    for z in [-.6,.36,1.55]:
        tube("15_DoorPanelSeam",S((.925,.45,z)),S((.925,.94,z)),.010,black)
    for z in [-.3,.83]:
        rounded_box("16_SlimFlushDoorHandle",S((.946,.991,z)),(.035,.039,.15),black,.008)
    rounded_box("17_CompactMirrorStalk",S((.89,1.17,-.7)),(.18,.065,.09),black,.017)
    rounded_box("18_AeroMirror",S((1.02,1.19,-.72)),(.22,.12,.19),cream,.044)
    # Three clean racing stripes that integrate with the sculpted doors.
    panel("19_CleanOrangeMotorsportSlash",[S((.956,.57,-.68)),S((.957,.66,-.57)),S((.934,.77,.56)),S((.935,.64,.63))],orange)
    panel("20_TealRallySweep",[S((.956,.50,-.46)),S((.954,.57,-.34)),S((.925,.62,1.10)),S((.927,.49,1.16))],aqua)
    rounded_box("21_DoorNumberBadge",S((.954,.86,-.06)),(.027,.23,.36),black,.014)
    rounded_box("22_DoorNumberAccent",S((.973,.86,-.06)),(.012,.15,.21),gold,.006)
    # Lens units wrap into curved corners.
    rounded_box("23_HeadlightGlass",S((.66,.835,-2.155)),(.32,.104,.085),glass,.037)
    rounded_box("24_HeadlightRunningLamp",S((.71,.85,-2.20)),(.23,.026,.037),lamps,.009)
    rounded_box("25_RearLED_LightCluster",S((.675,.81,2.083)),(.36,.11,.073),taillight,.020)
    rounded_box("26_RearLED_Accent",S((.74,.825,2.13)),(.16,.032,.028),gold,.008)

rounded_box("27_LowerFrontValance",(0,.485,-2.177),(1.47,.19,.22),black,.066)
rounded_box("28_FrontRadiatorOpening",(0,.72,-2.221),(.96,.23,.044),black,.03)
for k in range(10):
    rounded_box("29_FineIntakeSlat",(-.435+k*.097,.711,-2.251),(.027,.16,.028),light,.009)
rounded_box("30_FrontLowerSplitter",(0,.36,-2.28),(1.49,.055,.31),black,.02)
rounded_box("31_RearBumper",(0,.61,2.12),(1.47,.20,.18),light,.035)
rounded_box("32_RallyDiffuser",(0,.37,2.2),(1.32,.14,.20),black,.021)
for side in [-1,1]:
    rounded_box("33_RearWingSupport",(side*.55,1.64,1.69),(.085,.36,.14),black,.03)
    rounded_box("34_WingEndPlate",(side*.83,1.82,1.67),(.042,.16,.38),black,.017)
rounded_box("35_RallyAeroWing",(0,1.83,1.68),(1.70,.077,.33),cream,.022)
rounded_box("36_WingGurney",(0,1.86,1.86),(1.69,.03,.045),orange,.012)
rounded_box("37_RoofScoop",(0,1.65,-.19),(.42,.12,.36),cream,.048)
rounded_box("38_RoofScoopOpening",(0,1.675,-.372),(.31,.061,.023),black,.007)
rounded_box("39_HoodStripe",(0,1.005,-1.65),(.26,.016,.54),orange,.015)
rounded_box("40_HoodAirExtraction",(0,.99,-1.25),(.43,.019,.18),black,.01)
rounded_box("41_ExhaustTailpipeOuter",(.50,.37,2.225),(.18,.135,.20),light,.025)
rounded_box("42_ExhaustOpening",(.50,.37,2.336),(.116,.09,.01),black,.007)
# Final hand-edged smooth shading preserved; no photoreal textures, all geometry.
# Convert our Godot Y-up coordinates through Blender Z-up into glTF Y-up.
# R_x(+90) in Blender is the inverse of Blender->glTF (x,z,-y).
from mathutils import Matrix
axis_fix=Matrix.Rotation(pi/2,4,"X")
for ob in list(bpy.context.scene.objects):
    ob.matrix_world = axis_fix @ ob.matrix_world
bpy.ops.export_scene.gltf(filepath=OUT,export_format="GLB",use_selection=False,export_apply=True)
print("PIXEL_GARAGE_NEW_REAL_3D_BODY:",OUT,os.path.getsize(OUT),"bytes")
