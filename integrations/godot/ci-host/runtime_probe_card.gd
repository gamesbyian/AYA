@tool
extends "res://addons/AYA/aya_card.gd"

# Synthetic CI-host probe, deliberately OUTSIDE the reusable AYA addon.
# Emits a public, payload-free success/failure marker once after Android
# Godot scene construction. Never opens review or invokes a share target.
func _ready() -> void:
    super._ready()
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
        print("AYA_CI_GODOT_RUNTIME_READY")
    else:
        print("AYA_CI_GODOT_RUNTIME_FAIL")
        push_error("AYA card exists but has no visible Android viewport geometry")
