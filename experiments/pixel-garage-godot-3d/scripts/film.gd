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
    var track = color_material("#786d59")
    for i in range(180):
        var z = 190.0-float(i)*2.1
        for side in [-1.0,1.0]:
            var streak = cube(self,Vector3(path_x(z)+side*.89,0.008,z),Vector3(.23,.012,1.86),track)
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
        var distance = rng.randf_range(5.7,41.0)
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
    var white = color_material("#e6dcc4")
    var shade = color_material("#aebfb8")
    var ink = color_material("#1b2930")
    var dark = color_material("#101a22")
    var glass = color_material("#203d4a")
    var shine = color_material("#5ca5a8")
    var teal = color_material("#0dd0c2")
    var red = color_material("#f16438")
    var amber = color_material("#ffba67")
    car = Node3D.new()
    car.name = "PROCEDURAL_TRUE_3D_WRC_HATCHBACK"
    add_child(car)
    chassis = Node3D.new()
    chassis.name = "SuspensionAnimatedBody"
    car.add_child(chassis)
    # A section-based connected polygonal shell: shaped nose, long wheelbase, upright hatch.
    var stations = [
        [-2.20,0.59,0.60],[-2.05,0.75,0.74],[-1.65,0.86,0.92],
        [-1.05,0.92,1.01],[-0.40,0.91,1.04],[0.45,0.91,1.04],
        [1.27,0.90,1.02],[1.79,0.85,0.97],[2.10,0.75,0.79]]
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
    var front_high = -0.16
    var rear_high = 1.02
    var rear_low = 1.78
    var roof_y = 1.62
    polygon(chassis,[Vector3(-.78,1.10,front_low),Vector3(.78,1.10,front_low),Vector3(.69,roof_y,front_high),Vector3(-.69,roof_y,front_high)],glass)
    polygon(chassis,[Vector3(-.69,roof_y,rear_high),Vector3(.69,roof_y,rear_high),Vector3(.78,1.07,rear_low),Vector3(-.78,1.07,rear_low)],glass)
    polygon(chassis,[Vector3(-.69,roof_y,front_high),Vector3(.69,roof_y,front_high),Vector3(.69,roof_y,rear_high),Vector3(-.69,roof_y,rear_high)],white)
    for side in [-1.0,1.0]:
        var x=side
        polygon(chassis,[Vector3(x*.815,1.13,-.81),Vector3(x*.695,1.59,-.34),Vector3(x*.695,1.735,.36),Vector3(x*.815,1.13,.32)],glass)
        polygon(chassis,[Vector3(x*.817,1.13,.38),Vector3(x*.697,1.735,.43),Vector3(x*.697,1.735,1.26),Vector3(x*.803,1.13,1.60)],glass)
        polygon(chassis,[Vector3(x*.818,1.51,-.38),Vector3(x*.744,1.60,-.15),Vector3(x*.742,1.46,.25),Vector3(x*.818,1.51,.18)],shine)
        cube(chassis,Vector3(x*.817,1.27,.38),Vector3(.045,.72,.045),white)
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
        cube(chassis,Vector3(x*.84,1.49,1.63),Vector3(.12,.33,.10),dark)
        cube(chassis,Vector3(x*.64,.89,-2.226),Vector3(.34,.13,.05),shine)
        cube(chassis,Vector3(x*.68,.89,2.219),Vector3(.32,.15,.05),red)
        cube(chassis,Vector3(x*.77,.91,2.25),Vector3(.09,.07,.06),amber)
    # Signature roof scoop and rally wing—separate 3D volumes.
    cube(chassis,Vector3(0,1.69,0.0),Vector3(.58,.16,.43),white)
    cube(chassis,Vector3(0,1.70,-.23),Vector3(.49,.07,.042),dark)
    cube(chassis,Vector3(0,1.82,1.69),Vector3(1.67,.10,.31),white)
    cube(chassis,Vector3(0,1.86,1.88),Vector3(1.72,.035,.05),red)
    for side in [-1.0,1.0]:
        cube(chassis,Vector3(side*.80,1.81,1.72),Vector3(.07,.19,.37),dark)
    cube(chassis,Vector3(0,.71,-2.245),Vector3(.93,.22,.035),dark)
    for k in range(9):
        cube(chassis,Vector3(-.4+float(k)*.1,.70,-2.27),Vector3(.035,.17,.029),ink)
    cube(chassis,Vector3(0,.73,2.248),Vector3(.41,.10,.03),ink)

    # Recessed wheel wells and arched fender accents, all modeled as physical 3D rings.
    for side in [-1.0,1.0]:
        for wheel_z in [-1.27,1.27]:
            var recess=MeshInstance3D.new()
            var dark_disc=CylinderMesh.new()
            dark_disc.top_radius=.444
            dark_disc.bottom_radius=.444
            dark_disc.height=.028
            dark_disc.radial_segments=28
            recess.mesh=dark_disc
            recess.rotation.z=PI*.5
            recess.position=Vector3(side*.907,.40,wheel_z)
            recess.material_override=ink
            chassis.add_child(recess)
            var lip=MeshInstance3D.new()
            var tor=TorusMesh.new()
            tor.inner_radius=.405
            tor.outer_radius=.465
            tor.rings=7
            tor.ring_segments=28
            lip.mesh=tor
            lip.rotation.z=PI*.5
            lip.position=Vector3(side*.977,.40,wheel_z)
            lip.material_override=shade
            chassis.add_child(lip)
    # True roof surface with a slim contrasting graphic and aerodynamic rails.
    cube(chassis,Vector3(0,1.635,.44),Vector3(.90,.022,.75),ink)
    for side in [-1.0,1.0]:
        cube(chassis,Vector3(side*.67,1.632,.43),Vector3(.055,.045,1.26),shade)
    # Hood racing-number card and clear contrasting side numbers.
    cube(chassis,Vector3(0,1.022,-1.44),Vector3(.66,.018,.36),dark)
    for side in [-1.0,1.0]:
        cube(chassis,Vector3(side*.947,.94,.04),Vector3(.022,.21,.34),ink)

    # Actual tyres, forged spokes and wheel centres with independent rotation.
    for sign in [-1.0,1.0]:
        for z in [-1.27,1.27]:
            var hub = Node3D.new()
            hub.name = "WheelSpinningAndSuspending"
            hub.position=Vector3(sign*.95,.40,z)
            car.add_child(hub)
            wheels.append(hub)
            var tire = MeshInstance3D.new()
            var cyl = CylinderMesh.new()
            cyl.top_radius = .36
            cyl.bottom_radius = .36
            cyl.height = .26
            cyl.radial_segments = 20
            tire.mesh = cyl
            tire.rotation.z = PI*.5
            tire.material_override=dark
            hub.add_child(tire)
            for rr in [0.23,0.29]:
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
                var spoke=cube(hub,Vector3(sign*.153,cos(a)*.18,sin(a)*.18),Vector3(.028,.235,.041),white)
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
        cone.bottom_radius=.115-float(q)*.028
        cone.height=.84-float(q)*.16
        cone.radial_segments=8
        plume.mesh=cone
        plume.rotation.x=PI*.5
        plume.position.z=.32-float(q)*.12
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
    var z = 137.0-SPEED*t
    car.position = Vector3(path_x(z),.016+.014*sin(t*10.6),z)
    car.rotation.y=atan((path_x(z+1.0)-path_x(z-1.0))*.5)
    chassis.rotation.z=.010*sin(t*3.9)+.014*cos(t*.7)
    chassis.rotation.x=.007*sin(t*6.3)
    chassis.position.y=.013*sin(t*10.0)
    for i in range(wheels.size()):
        var w: Node3D=wheels[i]
        w.rotation.x=t*SPEED/.36
        w.position.y=.40+.016*sin(t*7.5+float(i)*1.4)
    var burst=(t>.24 and t<1.47) or (t>7.28 and t<8.32) or (t>12.61 and t<13.66)
    flame.visible=burst
    if burst:
        flame.scale=Vector3(1.0+.07*sin(t*42.0),1.0+.10*sin(t*54.0),.68+.13*sin(t*47.0))
    if t<2.0:
        caption.text="WHY DO RALLY CARS\\nSHOOT FLAMES?"
    elif t<5.0:
        caption.text="THE EXHAUST IS\\nINCREDIBLY HOT"
    elif t<10.0:
        caption.text="UNBURNED FUEL\\nCAN IGNITE"
    elif t<12.0:
        caption.text="ANTI-LAG CAN\\nMAKE IT LOUDER"
    else:
        caption.text="FIRE ON THE\\nOVER-RUN."
    var pos=Vector3(3.3,2.0,6.3)
    var look=Vector3(0,1.05,.35)
    if t<2.0:
        pos=Vector3(3.15,1.95,6.15)
        look=Vector3(.08,.96,.55)
    elif t<5.0:
        pos=Vector3(7.0,1.95,1.9)
        look=Vector3(.0,.98,.05)
    elif t<7.35:
        pos=Vector3(-3.9,1.82,-6.85)
        look=Vector3(0,1.02,-.42)
    elif t<9.40:
        pos=Vector3(2.45,1.14,5.7)
        look=Vector3(.38,.62,2.16)
    elif t<11.55:
        pos=Vector3(-5.3,2.12,3.8)
        look=Vector3(-.05,.95,.4)
    else:
        pos=Vector3(3.1,2.25,6.8+.45*(t-11.55))
        look=Vector3(0,1.01,.46)
    cam.global_position=car.to_global(pos)
    cam.look_at(car.to_global(look),Vector3.UP)
    cam.fov=41.0 if t>=7.35 and t<9.4 else 44.0
