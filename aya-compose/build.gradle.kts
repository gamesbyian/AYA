import org.gradle.api.publish.maven.MavenPublication

plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
    id("maven-publish")
}

group = "dev.aya"
version = "0.1.0-SNAPSHOT"

android {
    namespace = "dev.aya.compose"
    compileSdk = 35
    defaultConfig {
        minSdk = 23
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }
    buildFeatures { compose = true }
    publishing { singleVariant("release") { withSourcesJar() } }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}

dependencies {
    api(project(":aya"))
    // Pinned to a Compose generation compatible with this repository's
    // Android Gradle Plugin 8.7.3 / compileSdk 35 baseline.
    api(platform("androidx.compose:compose-bom:2024.12.01"))
    api("androidx.compose.ui:ui")
    api("androidx.compose.runtime:runtime-saveable")
    testImplementation("junit:junit:4.13.2")
}

afterEvaluate {
    publishing {
        publications {
            create<MavenPublication>("release") {
                from(components["release"])
                groupId = "dev.aya"
                artifactId = "aya-compose"
                version = project.version.toString()
            }
        }
        repositories {
            maven {
                name = "Staging"
                // Both AYA artifacts must be consumable from one local Maven repository.
                url = uri(rootDir.resolve("aya/build/staging-maven"))
            }
        }
    }
}
