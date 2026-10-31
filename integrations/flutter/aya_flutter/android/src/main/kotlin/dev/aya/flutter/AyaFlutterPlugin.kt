package dev.aya.flutter

import android.app.Activity
import dev.aya.android.AyaBundledLaunchResult
import dev.aya.android.AyaComponentAction
import io.flutter.embedding.engine.plugins.FlutterPlugin
import io.flutter.embedding.engine.plugins.activity.ActivityAware
import io.flutter.embedding.engine.plugins.activity.ActivityPluginBinding
import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel

/**
 * Flutter engine-scoped bridge. Only deliberate Dart calls open local AYA
 * question/review UI. No model, recipient/response listener or file importer.
 */
class AyaFlutterPlugin : FlutterPlugin, MethodChannel.MethodCallHandler, ActivityAware {
    private var channel: MethodChannel? = null
    private var activity: Activity? = null

    override fun onAttachedToEngine(binding: FlutterPlugin.FlutterPluginBinding) {
        channel = MethodChannel(binding.binaryMessenger, "dev.aya/flutter_handoff").also {
            it.setMethodCallHandler(this)
        }
    }

    override fun onDetachedFromEngine(binding: FlutterPlugin.FlutterPluginBinding) {
        channel?.setMethodCallHandler(null)
        channel = null
        activity = null
    }

    override fun onAttachedToActivity(binding: ActivityPluginBinding) {
        activity = binding.activity
    }

    override fun onDetachedFromActivityForConfigChanges() {
        activity = null
    }

    override fun onReattachedToActivityForConfigChanges(binding: ActivityPluginBinding) {
        activity = binding.activity
    }

    override fun onDetachedFromActivity() {
        activity = null
    }

    override fun onMethodCall(call: MethodCall, result: MethodChannel.Result) {
        if (call.method != "openHelp") {
            result.notImplemented()
            return
        }
        val args = call.arguments as? Map<*, *>
        if (args == null) {
            result.success(rejected("Invalid AYA request parameters."))
            return
        }
        if ((args.containsKey("guideAsset") && args["guideAsset"] !is String) ||
            (args.containsKey("question") && args["question"] !is String) ||
            (args.containsKey("screenName") && args["screenName"] != null &&
                args["screenName"] !is String) ||
            (args.containsKey("askQuestion") && args["askQuestion"] !is Boolean)) {
            result.success(rejected("Invalid AYA request parameter types."))
            return
        }
        val asset = args["guideAsset"] as? String ?: "aya-guide.md"
        val question = args["question"] as? String ?: ""
        val screen = args["screenName"] as? String
        val ask = args["askQuestion"] as? Boolean ?: false
        val host = activity
        if (host == null || host.isFinishing || host.isDestroyed) {
            result.success(rejected("An active Android host screen is required."))
            return
        }
        host.runOnUiThread {
            if (activity !== host || host.isFinishing || host.isDestroyed) {
                result.success(rejected("Android host screen is no longer active."))
                return@runOnUiThread
            }
            val local = try {
                AyaComponentAction.Help(
                    guideAsset = asset,
                    screenName = screen,
                    askQuestion = ask
                ).launch(host, text = question)
            } catch (_: Exception) {
                AyaBundledLaunchResult.Rejected("The local AYA review could not be opened.")
            }
            val value = when (local) {
                AyaBundledLaunchResult.QuestionOpened -> mapOf("status" to "question_opened")
                AyaBundledLaunchResult.PreviewOpened -> mapOf("status" to "review_opened")
                is AyaBundledLaunchResult.Rejected -> rejected(local.reason)
            }
            result.success(value)
        }
    }

    private fun rejected(reason: String): Map<String, String> =
        mapOf("status" to "rejected", "reason" to reason)
}
