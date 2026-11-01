extends "res://addons/AYA/aya_card.gd"

# Synthetic CI-host probe, deliberately OUTSIDE the reusable AYA addon.
# Emits a public, payload-free success/failure marker once after Android
# Godot scene construction. Never opens review or invokes a share target.
func _ready() -> void:
    super._ready()
    if OS.has_feature("android") and not Engine.is_editor_hint():
        call_deferred("_verify_native_card")

func _verify_native_card() -> void:
    var button := get_node_or_null("AYAButton") as Button
    var question := get_node_or_null("AYAQuestion") as TextEdit
    var native_ready := Engine.has_singleton("AYA")
    if native_ready and button != null and not button.disabled and question != null:
        print("AYA_CI_GODOT_RUNTIME_READY")
    else:
        print("AYA_CI_GODOT_RUNTIME_FAIL")
        push_error("AYA synthetic Godot Android card or native singleton is unavailable")
