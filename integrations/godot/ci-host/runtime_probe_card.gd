@tool
extends "res://addons/AYA/aya_card.gd"

# Synthetic CI-host probe, deliberately OUTSIDE the reusable AYA addon.
# Emits a public, payload-free success/failure marker once after Android
# Godot scene construction. Never opens review or invokes a share target.
var _synthetic_draw_count: int = 0

func _ready() -> void:
    # Fixture-only hypothesis based on upstream GLES emulator issue #74828:
    # opaque RGB10_A2 targets have historically failed on Android emulators,
    # while a transparent background can use an RGBA8 target.
    # This must not be applied to reusable AYA or real consuming projects.
    get_viewport().transparent_bg = true
    super._ready()
    queue_redraw()
    if OS.has_feature("android") and not Engine.is_editor_hint():
        call_deferred("_verify_native_card")

func _verify_native_card() -> void:
    # A node tree can be ready before Godot has submitted a single frame.
    # Only the disposable fixture waits for its first frame and checks bounds.
    await RenderingServer.frame_post_draw
    var button := get_node_or_null("AYAButton") as Button
    var question := get_node_or_null("AYAQuestion") as TextEdit
    var native_ready := Engine.has_singleton("AYA")
    if not native_ready or button == null or button.disabled or question == null:
        print("AYA_CI_GODOT_RUNTIME_FAIL")
        push_error("AYA synthetic Godot Android card or native singleton is unavailable")
        return
    var viewport_rect := get_viewport().get_visible_rect()
    var card_rect := get_global_rect()
    var button_rect := button.get_global_rect()
    var question_rect := question.get_global_rect()
    var geometry_ok := (
        card_rect.size.x >= 200.0 and card_rect.size.y >= 100.0
        and button_rect.size.x >= 44.0 and button_rect.size.y >= 24.0
        and question_rect.size.x >= 44.0 and question_rect.size.y >= 24.0
        and card_rect.intersects(viewport_rect)
        and button_rect.intersects(viewport_rect)
    )
    # Public geometry only, no input content or user/application data.
    print("AYA_CI_GODOT_GEOMETRY card=", card_rect.size,
          " button=", button_rect.size, " question=", question_rect.size,
          " viewport=", viewport_rect.size,
          " render_driver=", RenderingServer.get_current_rendering_driver_name())
    if geometry_ok:
        _capture_synthetic_viewport_stats()
        print("AYA_CI_GODOT_RUNTIME_READY")
    else:
        print("AYA_CI_GODOT_RUNTIME_FAIL")
        push_error("AYA card exists but has no visible Android viewport geometry")

# Deterministic background belongs to the disposable test *host* only.
# If these high-contrast bands never reach Godot's own ViewportTexture, the
# renderer/scene is not visually testable even though card nodes exist.
func _draw() -> void:
    _synthetic_draw_count += 1
    var midpoint: float = size.x * 0.5
    draw_rect(Rect2(0.0, 0.0, midpoint, size.y),
        Color(0.015, 0.015, 0.015, 1.0), true)
    draw_rect(Rect2(midpoint, 0.0, size.x - midpoint, size.y),
        Color(0.27, 0.32, 0.37, 1.0), true)


func _capture_synthetic_viewport_stats() -> void:
    # Synthetic fixture only: log pixel counts, never image bytes or user data.
    var source: Image = get_viewport().get_texture().get_image()
    if source == null or source.is_empty():
        print("AYA_CI_GODOT_FRAME dark=0 light=0 opaque=0 draws=",
              _synthetic_draw_count, " valid=0")
        return
    source.convert(Image.FORMAT_RGBA8)
    source.resize(64, 64, Image.INTERPOLATE_BILINEAR)
    var dark := 0
    var light := 0
    var opaque := 0
    for y in range(source.get_height()):
        for x in range(source.get_width()):
            var pixel: Color = source.get_pixel(x, y)
            if pixel.a < 0.5:
                continue
            opaque += 1
            var brightness: float = maxf(pixel.r, maxf(pixel.g, pixel.b))
            if brightness <= 0.08:
                dark += 1
            elif brightness >= 0.31:
                light += 1
    print("AYA_CI_GODOT_FRAME dark=", dark, " light=", light,
          " opaque=", opaque, " draws=", _synthetic_draw_count,
          " valid=", int(dark >= 16 and light >= 16))
