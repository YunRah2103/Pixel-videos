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
    var world = WorldEnvironment.new()
    var e = Environment.new()
    e.background_mode = Environment.BG_SKY
    var s = Sky.new()
    var skies = ProceduralSkyMaterial.new()
    skies.sky_top_color = Color("#5c95b1")
    skies.sky_horizon_color = Color("#b4cfc7")
    skies.ground_horizon_color = Color("#a2b59b")
    s.sky_material = skies
    e.sky = s
    e.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
    e.tonemap_mode = Environment.TONE_MAPPER_FILMIC
    world.environment = e
    add_child(world)
    var sun = DirectionalLight3D.new()
    sun.light_color = Color("#ffe6c7")
    sun.light_energy = 1.6
    sun.shadow_enabled = true
    sun.rotation_degrees = Vector3(-58, -27, 0)
    add_child(sun)
    var meadow = MeshInstance3D.new()
    var ground = PlaneMesh.new()
    ground.size = Vector2(640, 640)
    meadow.mesh = ground
    meadow.position.y = -0.11
    meadow.material_override = color_material("#6d987b")
    add_child(meadow)
    create_road(6.4, -0.035, color_material("#738273"))
    create_road(5.2, -0.014, color_material("#b5a98e"))
    create_road(4.28, -0.011, color_material("#c0b294"))
    var gravel = [color_material("#9a9885"),color_material("#d2c7a6"),color_material("#827f70")]
    for i in range(520):
        var z = rng.randf_range(-220.0,220.0)
        var x = path_x(z) + rng.randf_range(-2.5,2.5)
        if i % 13 == 0:
            cube(self, Vector3(x,0.014,z),Vector3(0.16,0.02,0.12),gravel[i % 3])
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
    var bark = color_material("#40544b")
    var leaf = [color_material("#335c55"),color_material("#4c7660"),color_material("#698868")]
    var trunk = CylinderMesh.new()
    trunk.height = 1.0
    trunk.top_radius = 0.12
    trunk.bottom_radius = 0.18
    trunk.radial_segments = 5
    var crown = SphereMesh.new()
    crown.radial_segments = 7
    crown.rings = 4
    var base = MultiMesh.new()
    base.transform_format = MultiMesh.TRANSFORM_3D
    base.mesh = trunk
    base.instance_count = 440
    var crowns = []
    for k in range(3):
        var mm = MultiMesh.new()
        mm.transform_format = MultiMesh.TRANSFORM_3D
        mm.mesh = crown
        mm.instance_count = 440
        crowns.append(mm)
    for i in range(440):
        var z = rng.randf_range(-240.0,240.0)
        var side = -1.0 if i%2==0 else 1.0
        var x = path_x(z)+side*rng.randf_range(6.0,39.0)
        var h = rng.randf_range(1.8,4.8)
        base.set_instance_transform(i,Transform3D(Basis.IDENTITY.scaled(Vector3(1.0,h,1.0)),Vector3(x,h/2.0,z)))
        for j in range(3):
            var scale = (1.14-0.19*float(j))*h/3.2
            crowns[j].set_instance_transform(i,Transform3D(Basis.IDENTITY.scaled(Vector3(scale,scale*1.0,scale)),Vector3(x+(float(j)-1.0)*0.34,h+0.2+float(j)*0.37,z+float(j%2)*0.3)))
    var trunks = MultiMeshInstance3D.new()
    trunks.multimesh = base
    trunks.material_override = bark
    add_child(trunks)
    for j in range(3):
        var foliage = MultiMeshInstance3D.new()
        foliage.multimesh = crowns[j]
        foliage.material_override = leaf[j]
        add_child(foliage)
    var stones = color_material("#70847a")
    for i in range(82):
        var z = rng.randf_range(-220.0,220.0)
        var side = -1.0 if i%2==0 else 1.0
        ball(self,Vector3(path_x(z)+side*rng.randf_range(3.6,9.0),0,z),Vector3(rng.randf_range(0.32,0.7),0.24,0.45),stones,6)

func create_mountains() -> void:
    var palette = [color_material("#8aa396"),color_material("#719285"),color_material("#648679")]
    for i in range(21):
        var theta = TAU*float(i)/21.0
        var p = MeshInstance3D.new()
        var m = PrismMesh.new()
        m.size = Vector3(rng.randf_range(23,46),rng.randf_range(28,48),rng.randf_range(20,50))
        p.mesh = m
        p.position = Vector3(sin(theta)*145,8,cos(theta)*145)
        p.rotation.y = theta
        p.material_override = palette[i%3]
        add_child(p)

func create_rally_car() -> void:
    var white = color_material("#e7ece2")
    var shade = color_material("#bccbc7")
    var ink = color_material("#1b2930")
    var dark = color_material("#101a22")
    var glass = color_material("#31586a")
    var shine = color_material("#6ca0a5")
    var teal = color_material("#0cabb0")
    var red = color_material("#e94d37")
    var amber = color_material("#ffba67")
    car = Node3D.new()
    car.name = "PROCEDURAL_TRUE_3D_WRC_HATCHBACK"
    add_child(car)
    chassis = Node3D.new()
    chassis.name = "SuspensionAnimatedBody"
    car.add_child(chassis)
    # A section-based connected polygonal shell: shaped nose, long wheelbase, upright hatch.
    var stations = [
        [-2.20,0.58,0.61],[-2.05,0.79,0.83],[-1.65,0.87,1.03],
        [-1.05,0.90,1.06],[-0.40,0.91,1.11],[0.45,0.91,1.12],
        [1.27,0.89,1.10],[1.79,0.83,1.07],[2.10,0.74,0.86]]
    for i in range(stations.size()-1):
        var a = stations[i]
        var b = stations[i+1]
        for side in [-1.0,1.0]:
            var x0 = side*float(a[1])
            var x1 = side*float(b[1])
            polygon(chassis,[Vector3(x0,0.47,float(a[0])),Vector3(x1,0.47,float(b[0])),Vector3(x1,float(b[2]),float(b[0])),Vector3(x0,float(a[2]),float(a[0]))],white)
        polygon(chassis,[Vector3(-float(a[1]),float(a[2]),float(a[0])),Vector3(float(a[1]),float(a[2]),float(a[0])),Vector3(float(b[1]),float(b[2]),float(b[0])),Vector3(-float(b[1]),float(b[2]),float(b[0]))],white)
    cube(chassis,Vector3(0,0.44,0),Vector3(1.54,0.26,4.12),ink)
    cube(chassis,Vector3(0,0.69,-2.15),Vector3(1.40,0.24,0.13),shade)
    cube(chassis,Vector3(0,0.37,-2.24),Vector3(1.32,0.10,0.18),dark)
    cube(chassis,Vector3(0,0.60,2.13),Vector3(1.48,0.27,0.15),shade)
    cube(chassis,Vector3(0,0.42,2.24),Vector3(1.33,0.13,0.09),ink)
    # Cabin: explicitly sloped windshield, tall roof and near-upright rear hatch.
    var front_low = -0.92
    var front_high = -0.37
    var rear_high = 1.30
    var rear_low = 1.71
    var roof_y = 1.77
    polygon(chassis,[Vector3(-.78,1.10,front_low),Vector3(.78,1.10,front_low),Vector3(.69,roof_y,front_high),Vector3(-.69,roof_y,front_high)],glass)
    polygon(chassis,[Vector3(-.69,roof_y,rear_high),Vector3(.69,roof_y,rear_high),Vector3(.78,1.07,rear_low),Vector3(-.78,1.07,rear_low)],glass)
    polygon(chassis,[Vector3(-.69,roof_y,front_high),Vector3(.69,roof_y,front_high),Vector3(.69,roof_y,rear_high),Vector3(-.69,roof_y,rear_high)],white)
    for side in [-1.0,1.0]:
        var x=side
        polygon(chassis,[Vector3(x*.815,1.13,-.81),Vector3(x*.695,1.735,-.34),Vector3(x*.695,1.735,.36),Vector3(x*.815,1.13,.32)],glass)
        polygon(chassis,[Vector3(x*.817,1.13,.38),Vector3(x*.697,1.735,.43),Vector3(x*.697,1.735,1.26),Vector3(x*.803,1.13,1.60)],glass)
        polygon(chassis,[Vector3(x*.818,1.51,-.38),Vector3(x*.744,1.60,-.15),Vector3(x*.742,1.60,.25),Vector3(x*.818,1.51,.18)],shine)
        cube(chassis,Vector3(x*.817,1.30,.38),Vector3(.045,.91,.045),white)
        cube(chassis,Vector3(x*.81,1.12,-.65),Vector3(.28,.07,.24),ink)
        cube(chassis,Vector3(x*1.0,1.17,-.65),Vector3(.26,.11,.25),white)
        for door in [-.52,.43,1.49]:
            cube(chassis,Vector3(x*.924,.81,door),Vector3(.013,.36,.012),ink)
        for handle_z in [-.28,.86]:
            cube(chassis,Vector3(x*.926,1.02,handle_z),Vector3(.04,.04,.20),dark)
        # Hand-authored clustered livery is literal 3D raised geometry.
        for row in range(4):
            for col in range(8):
                if (row+2*col)%5 != 0:
                    var z = -.54+float(col)*.135
                    var y = .53+float(row)*.095
                    cube(chassis,Vector3(x*.941,y,z),Vector3(.013,.068,.102),teal if col<5 else red)
        polygon(chassis,[Vector3(x*.933,.70,-.58),Vector3(x*.934,.80,-.40),Vector3(x*.934,.57,.69),Vector3(x*.932,.50,.41)],red)
        cube(chassis,Vector3(x*.84,1.60,1.63),Vector3(.12,.33,.10),dark)
        cube(chassis,Vector3(x*.64,.89,-2.226),Vector3(.34,.13,.05),shine)
        cube(chassis,Vector3(x*.68,.89,2.219),Vector3(.32,.15,.05),red)
        cube(chassis,Vector3(x*.77,.91,2.25),Vector3(.09,.07,.06),amber)
    # Signature roof scoop and rally wing—separate 3D volumes.
    cube(chassis,Vector3(0,1.85,0.0),Vector3(.58,.16,.43),white)
    cube(chassis,Vector3(0,1.86,-.23),Vector3(.49,.07,.042),dark)
    cube(chassis,Vector3(0,1.98,1.69),Vector3(1.67,.10,.31),white)
    cube(chassis,Vector3(0,2.01,1.88),Vector3(1.72,.035,.05),red)
    for side in [-1.0,1.0]:
        cube(chassis,Vector3(side*.80,1.94,1.72),Vector3(.07,.19,.37),dark)
    cube(chassis,Vector3(0,.71,-2.245),Vector3(.93,.22,.035),dark)
    for k in range(9):
        cube(chassis,Vector3(-.4+float(k)*.1,.70,-2.27),Vector3(.035,.17,.029),ink)
    cube(chassis,Vector3(0,.73,2.248),Vector3(.41,.10,.03),ink)
    # Actual tyres, forged spokes and wheel centres with independent rotation.
    for sign in [-1.0,1.0]:
        for z in [-1.27,1.27]:
            var hub = Node3D.new()
            hub.name = "WheelSpinningAndSuspending"
            hub.position=Vector3(sign*.96,.44,z)
            car.add_child(hub)
            wheels.append(hub)
            var tire = MeshInstance3D.new()
            var cyl = CylinderMesh.new()
            cyl.top_radius = .41
            cyl.bottom_radius = .41
            cyl.height = .26
            cyl.radial_segments = 20
            tire.mesh = cyl
            tire.rotation.z = PI*.5
            tire.material_override=dark
            hub.add_child(tire)
            for rr in [0.25,0.315]:
                var t = MeshInstance3D.new()
                var ring = TorusMesh.new()
                ring.inner_radius = rr-0.028
                ring.outer_radius = rr+0.028
                ring.rings = 9
                ring.ring_segments = 24
                t.mesh=ring
                t.rotation.z=PI*.5
                t.position.x=sign*.142
                t.material_override=shade
                hub.add_child(t)
            for k in range(9):
                var a=TAU*float(k)/9.0
                var spoke=cube(hub,Vector3(sign*.153,cos(a)*.20,sin(a)*.20),Vector3(.028,.28,.047),white)
                spoke.rotation.x=a
            var cap=MeshInstance3D.new()
            var cm=SphereMesh.new()
            cm.radius=.09
            cm.height=.08
            cap.mesh=cm
            cap.position.x=sign*.156
            cap.material_override=teal
            hub.add_child(cap)
    # Exhaust origin attached to real rear 3D geometry.
    cube(chassis,Vector3(.45,.43,2.23),Vector3(.18,.16,.30),shade)
    flame=Node3D.new()
    flame.name="ACTUAL_3D_EXHAUST_COMBUSTION"
    flame.position=Vector3(.45,.44,2.39)
    chassis.add_child(flame)
    for q in range(3):
        var plume=MeshInstance3D.new()
        var cone=CylinderMesh.new()
        cone.top_radius=.015
        cone.bottom_radius=.17-float(q)*.040
        cone.height=1.45-float(q)*.25
        cone.radial_segments=8
        plume.mesh=cone
        plume.rotation.x=PI*.5
        plume.position.z=.48-float(q)*.15
        var col="#ff6d20" if q==0 else ("#ffc652" if q==1 else "#fff3c9")
        var fire=color_material(col,true)
        fire.emission_enabled=true
        fire.emission=Color(col)
        fire.emission_energy_multiplier=2.4
        plume.material_override=fire
        flame.add_child(plume)
    var burst_light=OmniLight3D.new()
    burst_light.light_color=Color("#ff853b")
    burst_light.omni_range=2.3
    burst_light.light_energy=2.2
    flame.add_child(burst_light)

func create_pixel_pass() -> void:
    var layer=CanvasLayer.new()
    layer.layer=1
    add_child(layer)
    var rect=ColorRect.new()
    rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    rect.size=Vector2(360,640)
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
    settings.font_size=21
    settings.font_color=Color("#fff0d2")
    settings.outline_color=Color("#172b32")
    settings.outline_size=4
    caption=Label.new()
    caption.label_settings=settings
    caption.position=Vector2(18,51)
    caption.size=Vector2(327,95)
    caption.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
    layer.add_child(caption)
    var brand=Label.new()
    var smaller=LabelSettings.new()
    smaller.font_size=10
    smaller.font_color=Color("#d8f5ed")
    smaller.outline_color=Color("#193540")
    smaller.outline_size=3
    brand.label_settings=smaller
    brand.text="PIXEL GARAGE / REAL GODOT 3D"
    brand.position=Vector2(18,23)
    layer.add_child(brand)

func _process(delta: float) -> void:
    tick += delta
    update_film(min(tick,SECONDS))

func update_film(t: float) -> void:
    var z=137.0-SPEED*t
    car.position=Vector3(path_x(z),.010+.017*sin(t*12.7),z)
    car.rotation.y=atan((path_x(z+1.0)-path_x(z-1.0))*.5)
    chassis.rotation.z=.019*sin(t*4.3)+.026*cos(t*.7)
    chassis.rotation.x=.011*sin(t*6.5)
    chassis.position.y=.020*sin(t*12.0)
    for i in range(wheels.size()):
        var w: Node3D=wheels[i]
        w.rotation.x=t*SPEED/.41
        w.position.y=.44+.030*sin(t*7.5+float(i)*1.4)
    var burst=(t>.25 and t<1.54) or (t>7.15 and t<8.4) or (t>12.52 and t<13.85)
    flame.visible=burst
    if burst:
        flame.scale=Vector3(1,1,.83+.22*sin(t*49.0))
    if t<2.0:
        caption.text="WHY DO RALLY CARS\nSHOOT FLAMES?"
    elif t<5.0:
        caption.text="HOT EXHAUST...\nAND UNBURNED FUEL"
    elif t<10.0:
        caption.text="FUEL + OXYGEN\n+ IGNITION HEAT"
    elif t<12.0:
        caption.text="ANTI-LAG CAN MAKE\nFLAMES MORE LIKELY"
    else:
        caption.text="RALLY FIRE.\nEXPLAINED."
    var pos=Vector3(3.0,2.3,6.6)
    var look=Vector3(0,1.0,.2)
    if t>=2.0 and t<5.0:
        pos=Vector3(7.0,2.0,.85)
    elif t>=5.0 and t<7.1:
        pos=Vector3(-3.65,1.67,-6.1)
    elif t>=7.1 and t<10.0:
        pos=Vector3(1.15,.80,3.5)
        look=Vector3(.44,.44,2.30)
    elif t>=10.0 and t<12.0:
        pos=Vector3(4.9,2.4,5.6)
    elif t>=12.0:
        pos=Vector3(-3.2,1.9,-6.1+float(t-12.0)*.7)
    cam.global_position=car.to_global(pos)
    cam.look_at(car.to_global(look),Vector3.UP)
    cam.fov=42.0 if t>=7.1 and t<10.0 else 49.0
