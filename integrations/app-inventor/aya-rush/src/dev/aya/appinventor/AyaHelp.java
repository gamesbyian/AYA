package dev.aya.appinventor;

import android.os.Looper;
import android.content.pm.PackageInfo;
import com.google.appinventor.components.annotations.Asset;
import com.google.appinventor.components.annotations.Extension;
import com.google.appinventor.components.annotations.SimpleEvent;
import com.google.appinventor.components.annotations.SimpleFunction;
import com.google.appinventor.components.runtime.AndroidNonvisibleComponent;
import com.google.appinventor.components.runtime.ComponentContainer;
import com.google.appinventor.components.runtime.EventDispatcher;
import dev.aya.android.AyaBundledLaunchResult;
import dev.aya.android.AyaComponentAction;
import java.util.regex.Pattern;

/**
 * Minimal, Android-only MIT App Inventor block adapter for provider-neutral AYA.
 *
 * This is a source/packaging PROTOTYPE, not a tested App Inventor APK.
 * It never monitors an assistant's reply or handles model-generated outputs.
 * A consuming app must display its own card text and package a truthful guide.
 */
@Extension(description = "Reviewed, one-way Android Ask Your Agent help handoff. " +
    "The host must display its own instructions and bundle an exact-version AYA-RAS guide. " +
    "Requires a BUILT App Inventor APK; the AI Companion is unsupported.")
public final class AyaHelp extends AndroidNonvisibleComponent {
  private static final Pattern SAFE_GUIDE = Pattern.compile(
      "^[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*\\.md$"
  );
  private static final int MAX_SCREEN_NAME = 128;

  public AyaHelp(ComponentContainer container) {
    super(container.$form());
  }

  /**
   * Returns this installed application's package and version, for creating
   * the app-specific reference BEFORE the developer ships its final build.
   * This does not create or validate that reference.
   */
  @SimpleFunction(description = "Return the installed app package and version, for " +
      "preparing an exact-version host guide. Does not send information.")
  public String HostIdentity() {
    try {
      PackageInfo info = form.getPackageManager().getPackageInfo(form.getPackageName(), 0);
      if (info.versionName == null || info.versionName.isEmpty()) {
        LocalStatus("rejected", "Installed app version is unavailable.");
        return "";
      }
      return form.getPackageName() + "@" + info.versionName;
    } catch (Exception ignored) {
      LocalStatus("rejected", "Could not inspect installed app identity.");
      return "";
    }
  }

  /**
   * Existing host UI must show description, reference attachment disclosure,
   * output-use instructions, optional question and an accessible Ask button.
   *
   * guideAsset: media-file path actually present in Activity.assets, using
   * strict AYA-RAS metadata matching this installed package and version.
   * Empty question is a valid prefilled request; there is no second composer.
   */
  @SimpleFunction(description = "Open AYA's local editable help review for this app. " +
      "Requires an exact package/version-matched AYA-RAS guide in Android assets. " +
      "No data is sent to an assistant until the user deliberately chooses Share.")
  public void OpenHelp(@Asset String guideAsset, String screenName, String question) {
    if (guideAsset == null || !SAFE_GUIDE.matcher(guideAsset).matches()) {
      LocalStatus("rejected", "Choose a safe bundled Markdown guide path.");
      return;
    }
    if (screenName != null && screenName.length() > MAX_SCREEN_NAME) {
      LocalStatus("rejected", "Screen name exceeds the supported length.");
      return;
    }
    if (Looper.myLooper() != Looper.getMainLooper()) {
      form.runOnUiThread(() -> LocalStatus(
          "rejected", "OpenHelp must be called from the screen's UI thread."));
      return;
    }
    if (form.isFinishing() || form.isDestroyed()) {
      LocalStatus("rejected", "A live Android screen is required.");
      return;
    }
    try {
      AyaComponentAction.Help action =
          new AyaComponentAction.Help(guideAsset, screenName, false);
      AyaBundledLaunchResult result = action.launch(form, question == null ? "" : question);
      if (result instanceof AyaBundledLaunchResult.PreviewOpened) {
        LocalStatus("review_opened", "");
      } else if (result instanceof AyaBundledLaunchResult.QuestionOpened) {
        LocalStatus("question_opened", "");
      } else if (result instanceof AyaBundledLaunchResult.Rejected) {
        LocalStatus("rejected", ((AyaBundledLaunchResult.Rejected) result).getReason());
      } else {
        LocalStatus("rejected", "AYA returned an unknown local status.");
      }
    } catch (Exception ignored) {
      LocalStatus("rejected", "Could not open local AYA review in this Android build.");
    }
  }

  /**
   * Reports only native local question/review opening or rejection.
   * This NEVER confirms that an external app received any text or attachment.
   */
  @SimpleEvent(description = "Local AYA UI status: review_opened, question_opened, " +
      "or rejected with a reason. This event never reports an assistant's answer.")
  public void LocalStatus(String status, String reason) {
    EventDispatcher.dispatchEvent(this, "LocalStatus", status, reason);
  }
}
