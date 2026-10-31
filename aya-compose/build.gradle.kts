import org.gradle.api.publish.maven.MavenPublication

plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
    id("maven-publish")
}

group = "dev.aya"
version = providers.gradleProperty("aya.version").orNull ?: "0.1.0-SNAPSHOT"

android {
    namespace = "dev.aya.compose"
    compileSdk = 35
    defaultConfig { minSdk = 23 }
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
    api("androidx.compose.ui:ui:1.7.8")
    api("androidx.compose.runtime:runtime:1.7.8")
    implementation("androidx.compose.runtime:runtime-saveable:1.7.8")
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
                url = uri(rootDir.resolve("aya/build/staging-maven"))
            }
        }
    }
}
