extends SceneTree

# The Android exporter silently refuses to export on a Linux host if
# ETC2/ASTC texture import is disabled. Test Godot's effective ProjectSettings
# value rather than grepping a source file that its INI parser might ignore.
func _initialize() -> void:
    var key := "rendering/textures/vram_compression/import_etc2_astc"
    var enabled := bool(ProjectSettings.get_setting(key, false))
    print("AYA Godot Android export effective texture import: ", enabled)
    if not enabled:
        push_error("The Android export requires ETC2/ASTC import in project.godot")
        quit(1)
        return
    quit(0)
