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
    var question = card.get_node_or_null("AYAQuestion")
    if not question is TextEdit:
        push_error("AYA question input must accept multiline text")
        quit(4)
        return
    if not question.scroll_fit_content_height:
        push_error("AYA question must grow within its host layout")
        quit(5)
        return
    question.text = "First line of the question.\nSecond line with unicode: café."
    if not question.text.contains("\n") or not question.text.ends_with("café."):
        push_error("AYA multiline and unicode question draft changed")
        quit(6)
        return
    var invalid = scene.instantiate()
    invalid.output_instructions = ""
    root.add_child(invalid)
    await process_frame
    if invalid.get_node("AYAButton").disabled == false:
        push_error("AYA missing output-use instructions must fail closed")
        quit(7)
        return
    print("AYA Godot editor/source smoke: OK")
    quit(0)
