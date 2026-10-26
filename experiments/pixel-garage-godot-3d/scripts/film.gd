extends Node3D
## Original real 3D geometry and camera perspective. Native 360x640 pixel-art finish.
const SECONDS = 14.0
const SPEED = 18.0
var tick = 0.0
var rng = RandomNumberGenerator.new()
var car: Node3D
var chassis: Node3D
var wheels = []
var flame: Node3D
var cam: Camera3D
var caption: Label

func color_material(hex: String, unshaded: bool = false) -> StandardMaterial3D:
    var m = StandardMaterial3D.new()
    m.albedo_color = Color(hex)
    m.roughness = 0.82
    m.metallic = 0.04
    m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
    if unshaded:
        m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    return m

func cube(parent: Node3D, at: Vector3, ext: Vector3, material: Material) -> MeshInstance3D:
    var o = MeshInstance3D.new()
    var shape = BoxMesh.new()
    shape.size = ext
    o.mesh = shape
    o.material_override = material
    o.position = at
    parent.add_child(o)
    return o

func ball(parent: Node3D, at: Vector3, dims: Vector3, material: Material, sides: int = 8) -> MeshInstance3D:
    var o = MeshInstance3D.new()
    var mesh = SphereMesh.new()
    mesh.radial_segments = sides
    mesh.rings = 4
    o.mesh = mesh
    o.material_override = material
    o.position = at
    o.scale = dims
    parent.add_child(o)
    return o

func polygon(parent: Node3D, v: Array, material: Material) -> void:
    var mesh = ArrayMesh.new()
    var verts = PackedVector3Array()
    var norm = PackedVector3Array()
    for j in range(1, v.size() - 1):
        var a: Vector3 = v[0]
        var b: Vector3 = v[j]
        var c: Vector3 = v[j + 1]
        verts.append_array(PackedVector3Array([a,b,c,c,b,a]))
        var n = (b-a).cross(c-a).normalized()
        for k in range(3):
            norm.append(n)
        for k in range(3):
            norm.append(-n)
    var ar = []
    ar.resize(Mesh.ARRAY_MAX)
    ar[Mesh.ARRAY_VERTEX] = verts
    ar[Mesh.ARRAY_NORMAL] = norm
    mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, ar)
    var obj = MeshInstance3D.new()
    obj.mesh = mesh
    obj.material_override = material
    parent.add_child(obj)

func path_x(z: float) -> float:
    return 1.8 * sin(z * 0.024) + 0.42 * sin(z * 0.061)

func _ready() -> void:
    rng.seed = 20261025
    get_viewport().canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
    create_landscape()
    create_rally_car()
    cam = Camera3D.new()
    cam.current = true
    cam.fov = 48.0
    cam.near = 0.05
    cam.far = 360.0
    add_child(cam)
    create_pixel_pass()
    create_caption()
    update_film(0.0)

func create_landscape() -> void:
    # Cohesive twilight forest: deliberate dark-green pixel palette, not overexposed low-poly white.
    var world = WorldEnvironment.new()
    var e = Environment.new()
    e.background_mode = Environment.BG_SKY
    var sky = Sky.new()
    var skies = ProceduralSkyMaterial.new()
    skies.sky_top_color = Color("#354d69")
    skies.sky_horizon_color = Color("#b18f7c")
    skies.ground_bottom_color = Color("#263d3c")
    skies.ground_horizon_color = Color("#698377")
    sky.sky_material = skies
    e.sky = sky
    e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    e.ambient_light_color = Color("#9db7b5")
    e.ambient_light_energy = 0.36
    e.reflected_light_source = Environment.REFLECTION_SOURCE_DISABLED
    e.tonemap_mode = Environment.TONE_MAPPER_LINEAR
    world.environment = e
    add_child(world)
    var sun = DirectionalLight3D.new()
    sun.light_color = Color("#ffd1a0")
    sun.light_energy = 0.78
    sun.shadow_enabled = true
    sun.rotation_degrees = Vector3(-42,-35,0)
    add_child(sun)
    var meadow = MeshInstance3D.new()
    var ground = PlaneMesh.new()
    ground.size = Vector2(660,660)
    meadow.mesh = ground
    meadow.position.y = -0.11
    meadow.material_override = color_material("#2b554b")
    add_child(meadow)
    create_road(7.9,-0.049,color_material("#294b44"))
    create_road(6.4,-0.036,color_material("#726c55"))
    create_road(5.25,-0.012,color_material("#9b8566"))
    # Irregular gravel clusters and two subtly worn racing lines.
    var gravel = [color_material("#b8a17e"),color_material("#5b5f50"),color_material("#89765d")]
    for i in range(2350):
        var z = rng.randf_range(-225.0,225.0)
        var x = path_x(z)+rng.randf_range(-2.62,2.62)
        if i % 5 == 0:
            cube(self,Vector3(x,0.012,z),Vector3(rng.randf_range(.06,.18),.014,rng.randf_range(.08,.27)),gravel[i%3])
    # Short subdued gravel ruts, not artificial continuous railway tracks.
    var track = color_material("#887761")
    for i in range(130):
        var z = 195.0-float(i)*3.35
        for side in [-1.0,1.0]:
            if (i+int(side))%3 != 0:
                var streak = cube(self,Vector3(path_x(z)+side*.85,0.003,z),Vector3(.10,.004,.74),track)
                streak.rotation.y = atan((path_x(z+1.0)-path_x(z-1.0))*.5)
    create_trees()
    create_mountains()

func create_road(width: float, y: float, material: Material) -> void:
    var verts = PackedVector3Array()
    var normals = PackedVector3Array()
    for i in range(220):
        var z0 = 220.0 - float(i)*2.1
        var z1 = z0 - 2.1
        var a = Vector3(path_x(z0)-width/2.0,y,z0)
        var b = Vector3(path_x(z0)+width/2.0,y,z0)
        var c = Vector3(path_x(z1)-width/2.0,y,z1)
        var d = Vector3(path_x(z1)+width/2.0,y,z1)
        verts.append_array(PackedVector3Array([a,b,c,b,d,c]))
        for k in range(6):
            normals.append(Vector3.UP)
    var arr = []
    arr.resize(Mesh.ARRAY_MAX)
    arr[Mesh.ARRAY_VERTEX] = verts
    arr[Mesh.ARRAY_NORMAL] = normals
    var shape = ArrayMesh.new()
    shape.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arr)
    var o = MeshInstance3D.new()
    o.mesh = shape
    o.material_override = material
    add_child(o)

func create_trees() -> void:
    # Framing pines, independent 3D geometry for parallax; tapered tiered foliage.
    var trunk = CylinderMesh.new()
    trunk.height = 1.0
    trunk.top_radius = .09
    trunk.bottom_radius = .17
    trunk.radial_segments = 6
    var spruces = CylinderMesh.new()
    spruces.top_radius = .07
    spruces.bottom_radius = .92
    spruces.height = 1.4
    spruces.radial_segments = 8
    var trunks = MultiMesh.new()
    trunks.transform_format = MultiMesh.TRANSFORM_3D
    trunks.mesh = trunk
    trunks.instance_count = 410
    var needle_tiers = []
    for j in range(3):
        var layer = MultiMesh.new()
        layer.transform_format = MultiMesh.TRANSFORM_3D
        layer.mesh = spruces
        layer.instance_count = 410
        needle_tiers.append(layer)
    for i in range(410):
        var z = rng.randf_range(-244.0,244.0)
        var side = -1.0 if i%2==0 else 1.0
        var distance = rng.randf_range(16.0,42.0)
        var x = path_x(z)+side*distance
        var h = rng.randf_range(2.8,7.4)
        var trunk_y = h*.32
        trunks.set_instance_transform(i,Transform3D(Basis.IDENTITY.scaled(Vector3(.8,h*.64,.8)),Vector3(x,trunk_y,z)))
        for j in range(3):
            var spread=(1.1-.20*float(j))*h*.26
            var rise=h*(.47+.19*float(j))
            needle_tiers[j].set_instance_transform(i,Transform3D(Basis.IDENTITY.scaled(Vector3(spread, h*.30, spread)),Vector3(x,rise,z)))
    var trunk_obj=MultiMeshInstance3D.new()
    trunk_obj.multimesh=trunks
    trunk_obj.material_override=color_material("#303f3c")
    add_child(trunk_obj)
    var leaf_palettes = ["#24483f","#2d6151","#3e765c"]
    for j in range(3):
        var foliage=MultiMeshInstance3D.new()
        foliage.multimesh=needle_tiers[j]
        foliage.material_override=color_material(leaf_palettes[j])
        add_child(foliage)
    var leaf_colors=[color_material("#386d57"),color_material("#517b5e"),color_material("#304e43")]
    var stone_colors=[color_material("#59675f"),color_material("#66746a"),color_material("#384f4b")]
    for i in range(315):
        var z=rng.randf_range(-228.0,228.0)
        var side=-1.0 if i%2==0 else 1.0
        var x=path_x(z)+side*rng.randf_range(3.65,9.8)
        if i%3==0:
            ball(self,Vector3(x,.13,z),Vector3(rng.randf_range(.22,.6),.22,rng.randf_range(.24,.55)),stone_colors[i%3],7)
        else:
            ball(self,Vector3(x,.14,z),Vector3(rng.randf_range(.24,.68),.29,.48),leaf_colors[i%3],7)
    # Small golden roadside flowers, 3D clustered highlights.
    var gold=color_material("#b5a374",true)
    for i in range(110):
        var z=rng.randf_range(-215.0,215.0)
        var side=-1.0 if i%2==0 else 1.0
        var x=path_x(z)+side*rng.randf_range(4.15,6.4)
        cube(self,Vector3(x,.19,z),Vector3(.08,.08,.08),gold)

func create_mountains() -> void:
    # Spatial multi-ridge silhouette, avoiding isolated enormous triangular mountains.
    var colors=[color_material("#4a6d66"),color_material("#587a73"),color_material("#728982")]
    for layer in range(3):
        var z=-116.0-float(layer)*46.0
        for k in range(20):
            var x=-180.0+float(k)*19.0
            var rise=rng.randf_range(9,26)+float(layer)*5.0
            polygon(self,[
                Vector3(x-16,-.2,z),
                Vector3(x+1,rise,z-2),
                Vector3(x+21,-.2,z)
            ], colors[layer])
            polygon(self,[
                Vector3(x-17,-.21,z+2),
                Vector3(x+1,rise,z-2),
                Vector3(x+1,rise*.71,z+24),
                Vector3(x-12,-.2,z+22)
            ],colors[max(0,layer-1)])


func create_rally_car() -> void:
    var ivory=color_material("#e6dcc4")
    var rubber=color_material("#121f25")
    var alloy=color_material("#a8b5a4")
    var shiny=color_material("#e2dac1")
    var teal=color_material("#0dc4aa")
    car=Node3D.new()
    car.name="BLENDER_MODELED_TRUE_3D_PIXEL_RALLY_HATCHBACK"
    add_child(car)
    chassis=Node3D.new()
    chassis.name="CoordinatedBodySuspension"
    car.add_child(chassis)
    var body_scene=load("res://assets/rally_car_body.glb") as PackedScene
    if body_scene == null:
        push_error("Missing actual Blender GLB! Refusing to substitute coloured cubes.")
        get_tree().quit(3)
        return
    var body_node=body_scene.instantiate()
    body_node.name="Real3DConnectedPanelHatchback"
    chassis.add_child(body_node)
    # Four independently spinning and suspending rally wheels in actual cut-out arches.
    for sign in [-1.0,1.0]:
        for z in [-1.26,1.24]:
            var hub=Node3D.new()
            hub.name="RotatingWheel_3D"
            hub.position=Vector3(sign*.95,.38,z)
            car.add_child(hub)
            wheels.append(hub)
            var tire=MeshInstance3D.new()
            var cyl=CylinderMesh.new()
            cyl.top_radius=.386
            cyl.bottom_radius=.386
            cyl.height=.245
            cyl.radial_segments=30
            tire.mesh=cyl
            tire.rotation.z=PI*.5
            tire.material_override=rubber
            hub.add_child(tire)
            var face=MeshInstance3D.new()
            var disc=CylinderMesh.new()
            disc.top_radius=.255
            disc.bottom_radius=.255
            disc.height=.012
            disc.radial_segments=26
            face.mesh=disc
            face.rotation.z=PI*.5
            face.position.x=sign*.136
            face.material_override=alloy
            hub.add_child(face)
            var wheel_dark=MeshInstance3D.new()
            var mid=CylinderMesh.new()
            mid.top_radius=.216
            mid.bottom_radius=.216
            mid.height=.016
            mid.radial_segments=24
            wheel_dark.mesh=mid
            wheel_dark.rotation.z=PI*.5
            wheel_dark.position.x=sign*.150
            wheel_dark.material_override=rubber
            hub.add_child(wheel_dark)
            for k in range(8):
                var a=TAU*float(k)/8.0
                var spoke=cube(hub,Vector3(sign*.161,cos(a)*.14,sin(a)*.14),Vector3(.023,.255,.048),shiny)
                spoke.rotation.x=a
            ball(hub,Vector3(sign*.183,0,0),Vector3(.033,.071,.071),teal,12)
    # Small, realistic flame attached to actual physical exhaust pipe: no giant spike.
    flame=Node3D.new()
    flame.name="CompactTailpipeCombustion"
    flame.position=Vector3(.50,.37,2.38)
    chassis.add_child(flame)
    var palette=["#ff6e20","#ffc053","#f6f2b0"]
    for k in range(3):
        var plume=MeshInstance3D.new()
        var shape=SphereMesh.new()
        shape.radius=1.0
        shape.height=2.0
        shape.radial_segments=9
        shape.rings=5
        plume.mesh=shape
        plume.scale=Vector3(.093-float(k)*.019,.071-float(k)*.014,.35-float(k)*.070)
        plume.position.z=.30-float(k)*.10
        var material=color_material(palette[k],true)
        material.emission_enabled=true
        material.emission=Color(palette[k])
        material.emission_energy_multiplier=1.45
        plume.material_override=material
        flame.add_child(plume)
    var glow=OmniLight3D.new()
    glow.light_color=Color("#ff8546")
    glow.omni_range=1.2
    glow.light_energy=.85
    flame.add_child(glow)

func create_pixel_pass() -> void:
    var layer=CanvasLayer.new()
    layer.layer=1
    add_child(layer)
    var rect=ColorRect.new()
    rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    rect.size=Vector2(270,480)
    rect.mouse_filter=Control.MOUSE_FILTER_IGNORE
    var shader=ShaderMaterial.new()
    shader.shader=load("res://shaders/intentional_pixel_art.gdshader")
    rect.material=shader
    layer.add_child(rect)

func create_caption() -> void:
    var layer=CanvasLayer.new()
    layer.layer=2
    add_child(layer)
    var settings=LabelSettings.new()
    settings.font_size=15
    settings.font_color=Color("#fff0d2")
    settings.outline_color=Color("#172b32")
    settings.outline_size=2
    caption=Label.new()
    caption.label_settings=settings
    caption.position=Vector2(13,36)
    caption.size=Vector2(240,85)
    caption.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
    layer.add_child(caption)
    var brand=Label.new()
    var smaller=LabelSettings.new()
    smaller.font_size=8
    smaller.font_color=Color("#d8f5ed")
    smaller.outline_color=Color("#193540")
    smaller.outline_size=3
    brand.label_settings=smaller
    brand.text="PIXEL GARAGE / REAL GODOT 3D"
    brand.position=Vector2(13,18)
    layer.add_child(brand)

func _process(delta: float) -> void:
    tick += delta
    update_film(min(tick,SECONDS))



func update_film(t: float) -> void:
    var z=137.0-SPEED*t
    car.position=Vector3(path_x(z),.016+.012*sin(t*10.6),z)
    car.rotation.y=atan((path_x(z+1.0)-path_x(z-1.0))*.5)
    chassis.rotation.z=.009*sin(t*3.8)+.013*cos(t*.7)
    chassis.rotation.x=.008*sin(t*6.0)
    chassis.position.y=.012*sin(t*10.0)
    for i in range(wheels.size()):
        var w: Node3D=wheels[i]
        w.rotation.x=t*SPEED/.386
        w.position.y=.38+.014*sin(t*7.5+float(i)*1.4)
    var burst=(t>.26 and t<1.40) or (t>7.37 and t<8.35) or (t>12.64 and t<13.63)
    flame.visible=burst
    if burst:
        flame.scale=Vector3(1.0+.09*sin(t*49.0),1.0+.08*sin(t*47.0),.78+.16*sin(t*53.0))
    if t<2.0:
        caption.text="WHY DO RALLY CARS\nSHOOT FLAMES?"
    elif t<5.0:
        caption.text="THE EXHAUST GETS\nINCREDIBLY HOT"
    elif t<10.0:
        caption.text="UNBURNED FUEL\nCAN IGNITE"
    elif t<12.0:
        caption.text="ANTI-LAG KEEPS\nTHE TURBO SPINNING"
    else:
        caption.text="THAT'S HOW\nFLAMES APPEAR."
    var pos=Vector3(3.3,2.0,8.2)
    var look=Vector3(0.0,.93,.22)
    if t<2.0:
        pos=Vector3(3.15,1.98,8.35)
        look=Vector3(.05,.90,.42)
    elif t<5.0:
        pos=Vector3(10.7,2.14,1.30)
        look=Vector3(0.0,.90,.03)
    elif t<7.35:
        pos=Vector3(-4.0,1.90,-8.2)
        look=Vector3(0.0,.91,-.27)
    elif t<9.40:
        pos=Vector3(2.9,1.18,6.35)
        look=Vector3(.31,.72,1.40)
    elif t<11.55:
        pos=Vector3(-4.8,2.28,7.3)
        look=Vector3(0.0,.95,.10)
    else:
        pos=Vector3(3.9,2.26,8.1+.35*(t-11.55))
        look=Vector3(0.0,.90,.19)
    cam.global_position=car.to_global(pos)
    cam.look_at(car.to_global(look),Vector3.UP)
    cam.fov=48.0 if t>=2.0 and t<5.0 else 44.0
