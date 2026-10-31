@tool
extends EditorPlugin

var _exporter: AYAExportPlugin

func _enter_tree() -> void:
    _exporter = AYAExportPlugin.new()
    add_export_plugin(_exporter)

func _exit_tree() -> void:
    if _exporter != null:
        remove_export_plugin(_exporter)
        _exporter = null

class AYAExportPlugin extends EditorExportPlugin:
    func _get_name() -> String:
        return "AYA"

    func _supports_platform(platform: EditorExportPlatform) -> bool:
        return platform is EditorExportPlatformAndroid

    func _get_android_libraries(platform: EditorExportPlatform, debug: bool) -> PackedStringArray:
        if debug:
            return PackedStringArray([
                "AYA/bin/debug/aya-godot-debug.aar",
                "AYA/bin/debug/aya-debug.aar"
            ])
        return PackedStringArray([
            "AYA/bin/release/aya-godot-release.aar",
            "AYA/bin/release/aya-release.aar"
        ])

    func _get_android_dependencies(platform: EditorExportPlatform, debug: bool) -> PackedStringArray:
        return PackedStringArray([
            "androidx.core:core:1.15.0",
            "org.jetbrains.kotlin:kotlin-stdlib:2.0.21"
        ])
