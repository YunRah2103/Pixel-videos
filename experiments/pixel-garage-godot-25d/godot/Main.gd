extends Node3D
## Pixel Garage: true 3D-positioned 2D authored sprites, NOT a 3D-pixel filter.
## This shot timeline is deterministic: fixed 30fps, one shared vehicle-distance model.
const FPS := 30.0
const TOTAL_FRAMES := 450
const TRACK_END := -440.0
const PALETTE_DARK := Color("#1a2a36")

var hero: Sprite3D
var exhaust: Sprite3D
var camera: Camera3D
var caption: TextureRect
var caption_bg: ColorRect
var shot_label: Label
var frame_number := 0
var t := 0.0
var z_car := 0.0
var body_bounce := 0.0
var rng := RandomNumberGenerator.new()

func _ready() -> void:
    rng.seed = 20261026
    RenderingServer.set_default_clear_color(Color("#e8b98c"))
    _create_environment()
    _create_road()
    _create_forest()
    _create_car()
    _create_camera()
    _create_overlays()
    _step_frame()

func _tex(name: String) -> Texture2D:
    return load("res://assets/" + name + ".png") as Texture2D

func _sprite(name: String, pixel: float, pos: Vector3, parent_node: Node3D) -> Sprite3D:
    var s := Sprite3D.new()
    s.texture = _tex(name)
    s.pixel_size = pixel
    s.position = pos
    s.billboard = BaseMaterial3D.BILLBOARD_ENABLED
    s.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
    s.shaded = false
    s.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
    s.render_priority = 1
    parent_node.add_child(s)
    return s

func _road_centre(z: float) -> float:
    return 2.1 * sin(z * 0.018) + 0.65 * sin(z * 0.042)

func _create_environment() -> void:
    var world := WorldEnvironment.new()
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = Color("#eec898")
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color("#d6e4b1")
    env.ambient_light_energy = 1.0
    env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
    world.environment = env
    add_child(world)
    # The silhouette is an authored 2D sprite in a real distant 3D plane.
    var ridge := _sprite("mountains", 0.57, Vector3(0, 48, -340), self)
    ridge.scale = Vector3(1.5, 1.4, 1.0)

func _create_road() -> void:
    var ground_mesh := PlaneMesh.new()
    ground_mesh.size = Vector2(440, 800)
    var m_ground := StandardMaterial3D.new()
    m_ground.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    m_ground.albedo_texture = _tex("ground")
    m_ground.uv1_scale = Vector3(8, 42, 1)
    m_ground.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
    m_ground.cull_mode = BaseMaterial3D.CULL_DISABLED
    var ground := MeshInstance3D.new()
    ground.mesh = ground_mesh
    ground.material_override = m_ground
    ground.position = Vector3(0, -0.06, -180)
    add_child(ground)
    # SurfaceTool builds a genuine ribbon road in world space. It curves;
    # every car and verge object's X position comes from this same spline.
    var st := SurfaceTool.new()
    st.begin(Mesh.PRIMITIVE_TRIANGLES)
    var mat := StandardMaterial3D.new()
    mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    mat.albedo_texture = _tex("road")
    mat.uv1_scale = Vector3(1, 1, 1)
    mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
    mat.cull_mode = BaseMaterial3D.CULL_DISABLED
    for i in range(121):
        var za := 45.0 - float(i) * 4.0
        var zb := za - 4.0
        var xa := _road_centre(za)
        var xb := _road_centre(zb)
        _tri(st, Vector3(xa - 4.6, 0.01, za), Vector2(0, i*0.5), Vector3(xb-4.6,0.01,zb), Vector2(0,(i+1)*0.5), Vector3(xb+4.6,0.01,zb), Vector2(1,(i+1)*0.5))
        _tri(st, Vector3(xa-4.6,0.01,za), Vector2(0,i*0.5), Vector3(xb+4.6,0.01,zb), Vector2(1,(i+1)*0.5), Vector3(xa+4.6,0.01,za), Vector2(1,i*0.5))
    var road := MeshInstance3D.new()
    road.mesh = st.commit()
    road.material_override = mat
    add_child(road)

func _tri(st: SurfaceTool, a: Vector3, uv_a: Vector2, b: Vector3, uv_b: Vector2, c: Vector3, uv_c: Vector2) -> void:
    st.set_uv(uv_a); st.add_vertex(a)
    st.set_uv(uv_b); st.add_vertex(b)
    st.set_uv(uv_c); st.add_vertex(c)

func _create_forest() -> void:
    # Fixed seeded positions in 3D. The camera overtakes them by actual depth.
    for i in range(260):
        var z := rng.randf_range(TRACK_END, 50.0)
        var side := -1.0 if i % 2 == 0 else 1.0
        var lane_offset := rng.randf_range(6.0, 34.0)
        var x := _road_centre(z) + side * lane_offset
        var sz := rng.randf_range(0.60, 1.95)
        var pine := _sprite("pine_%d" % (i%6), .024, Vector3(x, 2.15*sz, z), self)
        pine.scale = Vector3(sz, sz, 1)
        pine.modulate = Color(1.0, 1.0, 1.0, 1.0)
    for i in range(320):
        var z := rng.randf_range(TRACK_END, 50.0)
        var side := -1.0 if i % 2 == 0 else 1.0
        var x := _road_centre(z) + side*rng.randf_range(5.5, 9.8)
        var sz := rng.randf_range(.55, 1.3)
        var bush := _sprite("bush_%d" % (i%5), .016, Vector3(x, .45*sz, z), self)
        bush.scale = Vector3(sz, sz, 1)

func _create_car() -> void:
    hero = _sprite("car_rear_34", .020, Vector3(0, 1.16, 0), self)
    hero.render_priority = 3
    exhaust = _sprite("flame", .015, Vector3(.65, .49, .14), self)
    exhaust.visible = false
    exhaust.render_priority = 4

func _create_camera() -> void:
    camera = Camera3D.new()
    camera.current = true
    camera.fov = 47.0
    camera.near = .1
    camera.far = 850.0
    add_child(camera)

func _create_overlays() -> void:
    var canvas := CanvasLayer.new()
    canvas.layer = 4
    add_child(canvas)
    var trim := ColorRect.new()
    trim.position = Vector2(0,0)
    trim.size = Vector2(360,5)
    trim.color = Color("#182b38")
    canvas.add_child(trim)
    caption_bg = ColorRect.new()
    caption_bg.position=Vector2(3, 548)
    caption_bg.size=Vector2(354, 30)
    caption_bg.color=Color(0.06,0.12,0.16,.58)
    canvas.add_child(caption_bg)
    caption = TextureRect.new()
    caption.position=Vector2(8,548)
    caption.size=Vector2(340,36)
    caption.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
    caption.stretch_mode=TextureRect.STRETCH_KEEP
    caption.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST
    canvas.add_child(caption)
    shot_label=Label.new()
    shot_label.position=Vector2(15,25)
    shot_label.add_theme_color_override("font_color",Color("#eaf4cd"))
    shot_label.add_theme_font_size_override("font_size",12)
    shot_label.text="PIXEL GARAGE  /  RALLY 07"
    canvas.add_child(shot_label)

func _is_flame(now: float) -> bool:
    return (now>0.58 and now<1.45) or (now>7.1 and now<8.35) or (now>10.7 and now<11.5) or (now>13.65 and now<14.33)

func _step_frame() -> void:
    t = float(frame_number)/FPS
    # Shared motion drives car, camera, wheels and exhaust. Never scroll a 2D background.
    z_car = -17.2 * t - 0.7*sin(t*2.1)
    var cx := _road_centre(z_car)
    body_bounce = 0.024*sin(t*27.0) + 0.018*sin(t*45.0)
    hero.position = Vector3(cx,1.16+body_bounce,z_car)
    exhaust.position = Vector3(cx-1.12, .63+body_bounce, z_car+.28)
    exhaust.visible = _is_flame(t)
    exhaust.scale = Vector3(.72+.19*sin(t*52.0),.72+.15*cos(t*47.0),1)
    caption.visible = false
    caption_bg.visible = false
    var target := Vector3(cx,1.08,z_car-2.0)
    var placement := Vector3(cx+5.3,3.0,z_car+12.2)
    var car_name := "car_rear_34"
    if t < 3.0:
        placement = Vector3(cx+5.1,2.8,z_car+12.4)
        target = Vector3(cx,1.1,z_car-2.8)
        car_name="car_rear_34"
    elif t<6.0:
        placement = Vector3(cx+11.7,2.45,z_car+2.5)
        target = Vector3(cx,1.0,z_car-2.1)
        car_name="car_side"
    elif t<10.0:
        placement = Vector3(cx+2.35,1.38,z_car+5.1)
        target = Vector3(cx-.8,.7,z_car)
        car_name="car_rear_34"
        caption.visible = true
        caption_bg.visible = true
        caption.texture = _tex("caption_flame")
    elif t<13.0:
        placement = Vector3(cx-7.5,2.7,z_car-6.8)
        target = Vector3(cx,1.2,z_car+.8)
        car_name="car_front_34"
        exhaust.visible = false
        caption.visible = true
        caption_bg.visible = true
        caption.texture = _tex("caption_antilag")
    else:
        placement = Vector3(cx+8.6,4.5,z_car+20.0)
        target = Vector3(cx,1.5,z_car-8.0)
        car_name="car_rear_34"
    # Sprite-frame wheel animation shares the exact same elapsed time as the car motion.
    if car_name in ["car_side", "car_front_34", "car_rear_34"]:
        car_name += "_%d" % (int(t*20.0) % 4)
    hero.texture=_tex(car_name)
    hero.rotation.z = .016*sin(t*2.2)
    camera.position=placement
    camera.look_at(target,Vector3.UP)
    # Preserve clean cut at final frame; no outro.

func _process(_delta: float) -> void:
    frame_number += 1
    if frame_number >= TOTAL_FRAMES:
        get_tree().quit()
        return
    _step_frame()