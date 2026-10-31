@tool
extends VBoxContainer
class_name AYACard

## Attach this script to a VBoxContainer to make a provider-neutral AYA card.
## An editor preview cannot launch Android or share private information.

signal local_status_changed(state: String, detail: String)

@export var guide_asset: String = "aya-guide.md"
@export var screen_name: String = "Game"
@export var title_text: String = "Ask Your Agent"
@export_multiline var description_text: String = "Ask about this game or screen."
@export_multiline var attachment_disclosure: String = "A game guide may be offered as a text attachment; your AI app may ignore it."
@export_multiline var output_instructions: String = "Read the advice and follow it in the game yourself; nothing is applied automatically."
@export var question_hint: String = "Your question (optional)"

var _input: LineEdit
var _button: Button
var _request_id: String

func _ready() -> void:
    if has_node("AYAQuestion"):
        return
    _request_id = str(get_instance_id())
    var heading := Label.new()
    heading.text = title_text
    heading.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    add_child(heading)

    for message in [
        description_text,
        attachment_disclosure,
        "After your agent replies: " + output_instructions
    ]:
        var detail := Label.new()
        detail.text = message
        detail.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
        add_child(detail)

    _input = LineEdit.new()
    _input.name = "AYAQuestion"
    _input.placeholder_text = question_hint
    add_child(_input)

    _button = Button.new()
    _button.name = "AYAButton"
    _button.text = "Ask Your Agent"
    _button.custom_minimum_size.y = 48.0
    add_child(_button)
    _button.pressed.connect(_on_ask_pressed)

    if Engine.is_editor_hint():
        _button.disabled = true
        _button.tooltip_text = "AYA editor preview; no handoff is performed."
    elif output_instructions.strip_edges().is_empty():
        _button.disabled = true
        _button.tooltip_text = "Host-specific instructions for using the result are required."
    elif not OS.has_feature("android") or not Engine.has_singleton("AYA"):
        _button.disabled = true
        _button.tooltip_text = "AYA requires the Android plugin in a Gradle-built APK."
    else:
        var plugin = Engine.get_singleton("AYA")
        plugin.aya_local_status.connect(_on_aya_local_status)

func _on_ask_pressed() -> void:
    if _button.disabled or not Engine.has_singleton("AYA"):
        return
    _button.disabled = true
    Engine.get_singleton("AYA").openHelp(
        _request_id, guide_asset, screen_name, _input.text, false
    )

func _on_aya_local_status(request_id: String, state: String, detail: String) -> void:
    if request_id != _request_id:
        return
    _button.disabled = false
    local_status_changed.emit(state, detail)
    # review_opened proves only a local privacy dialog opened.
