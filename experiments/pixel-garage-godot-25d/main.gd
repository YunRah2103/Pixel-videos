extends Node2D
## Two-dimensional art in layered, spatially different parallax planes.
## No 3D models and no post-process pixelation. All motion from one travel value.

const FPS: float = 30.0
const DURATION: float = 15.0
const TILE_W: float = 1800.0
const CAR_SCALE: float = 0.87
const LAYERS = ["sky", "mountains", "farforest", "nearforest", "road", "foreground"]
const DEPTH = [0.035, 0.12, 0.27, 0.56, 1.0, 1.26]

var pairs: Array = []
var body: Sprite2D
var wheels: Array[Sprite2D] = []
var flame: Sprite2D
var flame_frames: Array[Texture2D] = []
var title_label: Label
var subtitle_label: Label
var frame_num: int = 0
var world_travel: float = 0.0

func _ready() -> void:
    Engine.max_fps = 30
    for layer_name in LAYERS:
        var copies: Array[Sprite2D] = []
        var image_texture: Texture2D = load("res://assets/%s.png" % layer_name)
        for i in range(2):
            var s := Sprite2D.new()
            s.texture = image_texture
            s.centered = false
            s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
            s.z_index = LAYERS.find(layer_name) * 2
            add_child(s)
            copies.append(s)
        pairs.append(copies)
    for wx in [81.0, 244.0]:
        var w := Sprite2D.new()
        w.texture = load("res://assets/wheel.png")
        w.centered = true
        w.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
        w.z_index = 9
        add_child(w)
        wheels.append(w)
    body = Sprite2D.new()
    body.texture = load("res://assets/car_body.png")
    body.centered = false
    body.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    body.z_index = 10
    add_child(body)
    flame = Sprite2D.new()
    flame.centered = false
    flame.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    flame.z_index = 8
    add_child(flame)
    for k in range(4):
        flame_frames.append(load("res://assets/flame_%s.png" % k))
    var overlay := CanvasLayer.new()
    overlay.layer = 3
    add_child(overlay)
    title_label = Label.new()
    title_label.text = "PIXEL GARAGE   /   01"
    title_label.position = Vector2(19, 29)
    title_label.add_theme_font_size_override("font_size", 12)
    title_label.add_theme_color_override("font_color", Color("#253e47"))
    overlay.add_child(title_label)
    subtitle_label = Label.new()
    subtitle_label.text = "THE RALLY STAGE"
    subtitle_label.position = Vector2(19, 50)
    subtitle_label.add_theme_font_size_override("font_size", 16)
    subtitle_label.add_theme_color_override("font_color", Color("#fff2d9"))
    overlay.add_child(subtitle_label)
    _step(0.0)

func _process(_delta: float) -> void:
    frame_num += 1
    _step(float(frame_num) / FPS)
    if frame_num >= int(DURATION * FPS):
        get_tree().quit()

func _step(t: float) -> void:
    world_travel = 240.0 * t + 25.0 * sin(t * 0.4)
    for i in range(LAYERS.size()):
        var xx: float = -fposmod(world_travel * DEPTH[i], TILE_W)
        pairs[i][0].position = Vector2(round(xx), 0.0)
        pairs[i][1].position = Vector2(round(xx + TILE_W), 0.0)
    var car_scale: float = CAR_SCALE * (1.0 + 0.07 * sin(PI * minf(1.0, t / DURATION)))
    var bounce: float = round(1.3 * sin(TAU * t * 3.25) + 0.75 * sin(TAU * t * 5.7))
    var x: float = 39.0 + round(13.0 * sin(t * 0.6)) + round(4.0 * sin(t * 0.23))
    var car_pos := Vector2(x, 361.0 + bounce)
    for i in range(2):
        wheels[i].position = car_pos + Vector2([81.0, 244.0][i] * car_scale, 99.0 * car_scale)
        wheels[i].scale = Vector2.ONE * car_scale
        wheels[i].rotation = world_travel / (25.0 * car_scale)
    body.position = car_pos
    body.scale = Vector2.ONE * car_scale
    flame.position = car_pos + Vector2(-59.0 * car_scale, 93.0 * car_scale)
    flame.scale = Vector2.ONE * car_scale
    flame.texture = flame_frames[int(t * 15.0) % 4]
    flame.visible = _fire(t)
    subtitle_label.visible = t < 2.8

func _fire(t: float) -> bool:
    return (t >= 0.56 and t < 1.08) or (t >= 5.50 and t < 5.90) or (t >= 10.40 and t < 10.65) or (t >= 13.20 and t < 13.60)
