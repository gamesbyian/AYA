extends SceneTree

func _initialize() -> void:
    call_deferred("_check")

func _check() -> void:
    var scene = load("res://aya_smoke.tscn")
    if scene == null:
        push_error("AYA editor smoke scene did not load")
        quit(1)
        return
    var card = scene.instantiate()
    root.add_child(card)
    await process_frame
    var button = card.get_node_or_null("AYAButton")
    if button == null:
        push_error("AYA node failed to construct a button")
        quit(2)
        return
    if not button.disabled:
        push_error("AYA non-Android card must not be actionable")
        quit(3)
        return
    print("AYA Godot editor/source smoke: OK")
    quit(0)
