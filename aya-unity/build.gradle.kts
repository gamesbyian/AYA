plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "dev.aya.unity"
    compileSdk = 35
    defaultConfig { minSdk = 23 }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}

dependencies {
    // Canonical AYA runtime owns guide identity, review and Android sharing.
    implementation(project(":aya"))
}

tasks.register<Copy>("stageUnityPlugin") {
    dependsOn("assembleDebug", "assembleRelease", ":aya:assembleDebug", ":aya:assembleRelease")
    into(layout.buildDirectory.dir("unity-plugin/Plugins/Android"))
    // Keep build variants physically separate: copying all four AARs into
    // one Unity Assets/Plugins/Android folder would duplicate the same classes.
    from(layout.buildDirectory.dir("outputs/aar")) {
        include("aya-unity-debug.aar")
        into("debug")
    }
    from(project(":aya").layout.buildDirectory.dir("outputs/aar")) {
        include("aya-debug.aar")
        into("debug")
    }
    from(layout.buildDirectory.dir("outputs/aar")) {
        include("aya-unity-release.aar")
        into("release")
    }
    from(project(":aya").layout.buildDirectory.dir("outputs/aar")) {
        include("aya-release.aar")
        into("release")
    }
}
