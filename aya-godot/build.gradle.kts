plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "dev.aya.godot"
    compileSdk = 35
    defaultConfig { minSdk = 24 }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}

dependencies {
    compileOnly("org.godotengine:godot:4.5.1.stable")
    implementation(project(":aya"))
}

tasks.register<Copy>("stageGodotAddon") {
    dependsOn("assembleDebug", "assembleRelease", ":aya:assembleDebug", ":aya:assembleRelease")
    into(layout.buildDirectory.dir("godot-addon/AYA"))
    from(rootDir.resolve("integrations/godot/addons/AYA")) {
        include("plugin.cfg", "export_plugin.gd", "aya_card.gd")
    }
    from(layout.buildDirectory.dir("outputs/aar")) {
        include("aya-godot-debug.aar")
        into("bin/debug")
    }
    from(layout.buildDirectory.dir("outputs/aar")) {
        include("aya-godot-release.aar")
        into("bin/release")
    }
    from(project(":aya").layout.buildDirectory.dir("outputs/aar")) {
        include("aya-debug.aar")
        into("bin/debug")
    }
    from(project(":aya").layout.buildDirectory.dir("outputs/aar")) {
        include("aya-release.aar")
        into("bin/release")
    }
}
