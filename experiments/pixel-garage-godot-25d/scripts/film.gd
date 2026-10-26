extends Node3D
## Genuine Godot 3D depth using authored pixel sprite artwork; NEVER a low-poly filter.
const SECONDS := 14.0
const SPEED := 15.5
var time := 0.0
var car: Node3D
var main_sprite: Sprite3D
var flame: Sprite3D
var dust: Sprite3D
var camera: Camera3D
var captions: Label
var car_textures: Dictionary = {}
var rng := RandomNumberGenerator.new()

func tex(file: String) -> Texture2D:
    return load("res://assets/"+file) as Texture2D

func track_x(z: float) -> float:
    return 1.5*sin(z*.020)+.3*sin(z*.044)

func sprite(file: String,parent: Node3D,p: Vector3,px: float=.014) -> Sprite3D:
    var a=Sprite3D.new()
    a.texture=tex(file)
    a.pixel_size=px
    a.texture_filter=BaseMaterial3D.TEXTURE_FILTER_NEAREST
    a.shaded=false
    a.billboard=BaseMaterial3D.BILLBOARD_ENABLED
    a.alpha_cut=SpriteBase3D.ALPHA_CUT_DISCARD
    a.position=p
    parent.add_child(a)
    return a

func plain(color: String) -> StandardMaterial3D:
    var m=StandardMaterial3D.new()
    m.albedo_color=Color(color)
    m.roughness=.9
    m.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
    return m

func _ready() -> void:
    rng.seed=20261026
    get_viewport().canvas_item_default_texture_filter=Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
    build_sky()
    build_road()
    build_forest()
    build_car()
    camera=Camera3D.new()
    camera.current=true
    camera.fov=48.
    camera.near=.05
    camera.far=360.
    add_child(camera)
    build_captions()
    animate_scene(0.)

func build_sky() -> void:
    var env=WorldEnvironment.new()
    var e=Environment.new()
    e.background_mode=Environment.BG_SKY
    var sky=Sky.new()
    var mat=ProceduralSkyMaterial.new()
    mat.sky_top_color=Color("#264b63")
    mat.sky_horizon_color=Color("#e3a279")
    mat.ground_horizon_color=Color("#597a76")
    sky.sky_material=mat
    e.sky=sky
    e.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
    e.ambient_light_color=Color("#ffcb98")
    e.ambient_light_energy=.32
    e.tonemap_mode=Environment.TONE_MAPPER_LINEAR
    env.environment=e
    add_child(env)

func build_road() -> void:
    var m=StandardMaterial3D.new()
    m.albedo_texture=tex("gravel.png")
    m.texture_filter=BaseMaterial3D.TEXTURE_FILTER_NEAREST
    m.uv1_scale=Vector3(5,50,1)
    m.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
    var verts=PackedVector3Array()
    var uvs=PackedVector2Array()
    var normals=PackedVector3Array()
    for k in range(265):
        var z=-290.+float(k)*2.3
        var zz=z+2.3
        var pts=[
            Vector3(track_x(z)-3.6,.008,z),
            Vector3(track_x(z)+3.6,.008,z),
            Vector3(track_x(zz)-3.6,.008,zz),
            Vector3(track_x(zz)+3.6,.008,zz)
        ]
        for n in [0,2,1,1,2,3]:
            verts.append(pts[n])
            normals.append(Vector3.UP)
            uvs.append(Vector2(0. if n%2==0 else 1.,(float(k)+(1. if n>=2 else 0.))/250.))
    var array=[]
    array.resize(Mesh.ARRAY_MAX)
    array[Mesh.ARRAY_VERTEX]=verts
    array[Mesh.ARRAY_NORMAL]=normals
    array[Mesh.ARRAY_TEX_UV]=uvs
    var built=ArrayMesh.new()
    built.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,array)
    var surface=MeshInstance3D.new()
    surface.name="TRUE_3D_PERSPECTIVE_GRAVEL_ROAD"
    surface.mesh=built
    surface.material_override=m
    add_child(surface)
    var ground=MeshInstance3D.new()
    var mesh=PlaneMesh.new()
    mesh.size=Vector2(650,650)
    ground.mesh=mesh
    ground.position.y=-.022
    ground.material_override=plain("#31594e")
    add_child(ground)

func build_forest() -> void:
    for k in range(260):
        var z=rng.randf_range(-285.,310.)
        var side=-1. if k%2==0 else 1.
        var x=track_x(z)+side*rng.randf_range(5.6,43.)
        var scale=rng.randf_range(.73,1.50)
        sprite("pine_%d.png"%(k%7),self,Vector3(x,1.40*scale,z),.014*scale)
    # Real depth-separated mountain planes; not 2D screen translations.
    for layer in range(3):
        var z=-205.-float(layer)*33.
        var mountain=sprite("mountains_far.png" if layer!=1 else "mountains_near.png",
            self,Vector3(0,19.+float(layer)*3.,z),.27+float(layer)*.07)
        mountain.billboard=BaseMaterial3D.BILLBOARD_FIXED_Y
    for j in range(165):
        var z=rng.randf_range(-280.,298.)
        var side=-1. if j%2==0 else 1.
        var x=track_x(z)+side*rng.randf_range(3.85,6.2)
        var b=sprite("dust.png",self,Vector3(x,.26,z),.008*rng.randf_range(.6,.95))
        b.modulate=Color("#377461")

func build_car() -> void:
    car=Node3D.new()
    car.name="2_5D_HandDrawnRallyHatchback"
    add_child(car)
    for a in ["rear3q","side","front3q"]:
        var frames=[]
        for i in range(8):
            frames.append(tex("car_%s_%d.png"%[a,i]))
        car_textures[a]=frames
    main_sprite=sprite("car_rear3q_0.png",car,Vector3(0,1.04,0),.015)
    flame=sprite("flame.png",car,Vector3(.98,.68,.06),.009)
    flame.visible=false
    dust=sprite("dust.png",car,Vector3(-1.65,.25,.28),.014)
    dust.modulate=Color(1.,1.,1.,.64)

func build_captions() -> void:
    var layer=CanvasLayer.new()
    layer.layer=2
    add_child(layer)
    var style=LabelSettings.new()
    style.font_size=18
    style.font_color=Color("#fff1c6")
    style.outline_color=Color("#1c2c3a")
    style.outline_size=3
    captions=Label.new()
    captions.label_settings=style
    captions.position=Vector2(20,66)
    captions.size=Vector2(325,110)
    captions.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
    layer.add_child(captions)
    var small=LabelSettings.new()
    small.font_size=10
    small.font_color=Color("#f1d9a9")
    small.outline_color=Color("#163445")
    small.outline_size=2
    var signature=Label.new()
    signature.label_settings=small
    signature.text="PIXEL GARAGE / RALLY SCIENCE"
    signature.position=Vector2(20,40)
    layer.add_child(signature)

func _process(delta:float) -> void:
    time+=delta
    animate_scene(min(time,SECONDS))

func animate_scene(t:float) -> void:
    var z=145.-SPEED*t
    car.position=Vector3(track_x(z),.02+.022*sin(t*11.2),z)
    car.rotation.y=-atan((track_x(z+1.)-track_x(z-1.))*.5)
    main_sprite.position.y=1.04+.024*sin(t*9.1)
    main_sprite.rotation.z=.009*sin(t*4.7)
    var shot="rear3q"
    var cam_pos=Vector3(5.9,2.45,10.5)
    var focal=Vector3(0,1.05,0)
    if t<3.:
        captions.text="WHY DO RALLY CARS\nSHOOT FLAMES?"
    elif t<6.:
        shot="side"
        cam_pos=Vector3(11.1,2.65,1.7)
        captions.text="THE EXHAUST GETS\nSERIOUSLY HOT"
    elif t<10.:
        cam_pos=Vector3(3.15,1.61,5.3)
        focal=Vector3(.55,.68,.1)
        captions.text="UNBURNED FUEL\nCAN IGNITE"
    elif t<13.:
        shot="front3q"
        cam_pos=Vector3(-4.2,2.15,-7.3)
        captions.text="ANTI-LAG CAN\nADD THE FIRE"
    else:
        cam_pos=Vector3(4.8,2.2,11.2)
        captions.text="RALLY FLAMES.\nEXPLAINED."
    main_sprite.texture=car_textures[shot][int(t*11.7)%8]
    var firing=(t>.31 and t<1.20) or (t>7.23 and t<8.) or (t>13.16 and t<13.78)
    flame.visible=firing and shot=="rear3q"
    if firing:
        flame.scale=Vector3(.94+.12*sin(t*37),.94,.93+.18*sin(t*39))
    dust.visible=(t>=3. and t<=6.) or (t>10.2 and t<12.)
    camera.global_position=car.to_global(cam_pos)
    camera.look_at(car.to_global(focal),Vector3.UP)
    camera.fov=45. if t>=6. and t<10. else 48.
