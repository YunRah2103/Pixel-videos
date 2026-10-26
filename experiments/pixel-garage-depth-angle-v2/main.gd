extends Node3D
## True perspective using 2D artwork in 3D positions. Never a 3D car model.
## The gravel is a textured surface; the car, shrubs, rocks and pines are original Sprite3D images.
const FPS := 30.0
const LENGTH := 8.0
const SPEED := 4.8
var frame: int = 0
var cam: Camera3D
var car: Sprite3D
var flame: Sprite3D
var dust: Sprite3D
var car_sheets: Array[Texture2D] = []
var flame_sheets: Array[Texture2D] = []
var dust_sheets: Array[Texture2D] = []

func tex(name: String) -> Texture2D:
    return load("res://assets/%s.png" % name)

func make_surface(name: String, repeat_x: float, repeat_y: float) -> StandardMaterial3D:
    var m := StandardMaterial3D.new()
    m.albedo_texture = tex(name)
    m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
    m.uv1_scale = Vector3(repeat_x, repeat_y, 1.0)
    m.cull_mode = BaseMaterial3D.CULL_DISABLED
    return m

func floor_plane(width: float, height: float, level: float, name: String, u: float, v: float) -> void:
    var mesh := PlaneMesh.new()
    mesh.size = Vector2(width, height)
    var obj := MeshInstance3D.new()
    obj.mesh = mesh
    obj.material_override = make_surface(name, u, v)
    obj.position = Vector3(0, level, -170.0)
    add_child(obj)

func sprite_at(name: String, x: float, z: float, physical_h: float, mirror: bool = false) -> Sprite3D:
    var sp := Sprite3D.new()
    sp.texture = tex(name)
    sp.billboard = BaseMaterial3D.BILLBOARD_ENABLED
    sp.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
    sp.shaded = false
    sp.pixel_size = physical_h / float(sp.texture.get_height())
    sp.position = Vector3(x, physical_h * 0.5, z)
    sp.flip_h = mirror
    sp.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
    add_child(sp)
    return sp

func _ready() -> void:
    Engine.max_fps = 30
    var background_layer := CanvasLayer.new()
    background_layer.layer = -100
    add_child(background_layer)
    var back := TextureRect.new()
    back.texture = tex("sky")
    back.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    back.size = Vector2(360, 640)
    background_layer.add_child(back)
    floor_plane(220.0, 440.0, -0.12, "grass", 34.0, 76.0)
    floor_plane(8.3, 440.0, -0.085, "gravel", 1.0, 106.0)
    var rng := RandomNumberGenerator.new()
    rng.seed = 20261026
    for i in range(105):
        var z: float = 24.0 - float(i) * 2.74
        var side: float = -1.0 if i % 2 == 0 else 1.0
        var lateral: float = side * rng.randf_range(5.5, 17.0)
        var ht: float = rng.randf_range(5.8, 11.8)
        sprite_at("pine_%d" % (i % 5), lateral, z, ht, i % 3 == 0)
        if i % 2 == 0:
            sprite_at("shrub_%d" % (int(i / 2) % 4), side * rng.randf_range(4.7, 8.1), z + rng.randf_range(-1.2, 1.2), rng.randf_range(.58, 1.07))
        if i % 4 == 0:
            sprite_at("rock_%d" % (int(i / 4) % 4), side * rng.randf_range(4.7, 6.5), z + .7, rng.randf_range(.37, .67))
    for i in range(8):
        car_sheets.append(tex("rally_%d" % i))
    for i in range(4):
        flame_sheets.append(tex("flame_%d" % i))
        dust_sheets.append(tex("dust_%d" % i))
    car = sprite_at("rally_0", 0, -7.5, 3.25)
    flame = sprite_at("flame_0", -1.33, -7.39, .60)
    dust = sprite_at("dust_0", -.6, -5.7, .6)
    cam = Camera3D.new()
    cam.fov = 47
    cam.near = .08
    cam.far = 500.0
    cam.current = true
    add_child(cam)
    update_scene(0)

func _process(_delta: float) -> void:
    frame += 1
    update_scene(float(frame) / FPS)
    if frame >= int(LENGTH * FPS):
        get_tree().quit()

func update_scene(t: float) -> void:
    var travel: float = SPEED * t
    var lean: float = .22 * sin(t * .7)
    var bounce: float = .026 * sin(t * 19) + .014 * sin(t * 31)
    car.position = Vector3(lean, 1.6 + bounce, -7.5 - travel)
    car.texture = car_sheets[int(floor(travel * 4.3)) % 8]
    flame.position = Vector3(lean - 1.33, .83 + bounce, -7.39 - travel)
    flame.texture = flame_sheets[int(floor(t * 23)) % 4]
    flame.visible = (t > .55 and t < .83) or (t > 4.7 and t < 4.98) or (t > 7.07 and t < 7.3)
    dust.position = Vector3(lean - .6, .38, -5.7 - travel)
    dust.texture = dust_sheets[int(floor(t * 8)) % 4]
    dust.visible = t > .2
    cam.position = Vector3(-.7 + .28 * sin(t * .52), 3.9 + .05 * sin(t * 3), 8.3 - travel)
    cam.look_at(Vector3(.3 + lean * .4, 1.0, -12.4 - travel), Vector3.UP)
