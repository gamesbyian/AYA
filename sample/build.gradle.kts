plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}
android {
    namespace = "dev.aya.sample"
    compileSdk = 35
    defaultConfig {
        applicationId = "dev.aya.sample"
        minSdk = 23
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}
dependencies {
    if (providers.gradleProperty("aya.consumePublished").orNull == "true") {
        implementation("dev.aya:aya-android:0.1.0-SNAPSHOT")
    } else {
        implementation(project(":aya"))
    }
}
