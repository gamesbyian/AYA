import { requireOptionalNativeModule } from 'expo-modules-core';
import { Platform } from 'react-native';

export type AyaLocalStatus = 'question_opened' | 'review_opened' | 'rejected';
export type AyaLocalResult = {
  status: AyaLocalStatus;
  reason?: string;
};

/** Host-owned question and public screen hint. Never include secret app state. */
export type AyaOpenHelpOptions = {
  question?: string;
  guideAsset?: string;
  screenName?: string | null;
  askQuestion?: boolean;
};

type NativeAya = {
  openHelp(
    guideAsset: string,
    screenName: string | null,
    question: string,
    askQuestion: boolean
  ): Promise<unknown>;
};

// Optional linking: unsupported platforms and Expo Go fail locally and visibly.
const nativeModule = Platform.OS === 'android'
  ? requireOptionalNativeModule<NativeAya>('AyaExpo')
  : null;

const reject = (reason: string): AyaLocalResult => ({
  status: 'rejected',
  reason,
});

export async function openAyaHelp(
  options: AyaOpenHelpOptions = {}
): Promise<AyaLocalResult> {
  if (Platform.OS !== 'android') {
    return reject('AYA Android sharing is not available on this platform.');
  }
  if (nativeModule === null) {
    return reject('AYA native module is missing. Build an Android development client or APK; Expo Go cannot load it.');
  }
  const guideAsset = options.guideAsset ?? 'aya-guide.md';
  // No traversal, ambiguous separators, resource schemes or implicit URL reads.
  if (!/^[A-Za-z0-9_-]+(?:\/[A-Za-z0-9_-]+)*\.md$/.test(guideAsset)) {
    return reject('Invalid bundled AYA guide asset path.');
  }
  if (typeof options.question !== 'undefined' && typeof options.question !== 'string') {
    return reject('Question must be text.');
  }
  if (options.screenName != null && typeof options.screenName !== 'string') {
    return reject('Screen name must be text.');
  }
  if (options.askQuestion != null && typeof options.askQuestion !== 'boolean') {
    return reject('askQuestion must be a boolean.');
  }
  try {
    const value = await nativeModule.openHelp(
      guideAsset, options.screenName ?? null,
      options.question ?? '',
      // Bare actions are question-first; an explicitly supplied question
      // (including an intentionally empty host-owned field) already has a
      // composer. A caller can override either behavior deliberately.
      options.askQuestion ?? (options.question === undefined)
    );
    if (typeof value !== 'object' || value === null || !('status' in value)) {
      return reject('Unexpected response from AYA Android module.');
    }
    const result = value as Record<string, unknown>;
    if (result.status === 'question_opened' || result.status === 'review_opened') {
      return { status: result.status };
    }
    if (result.status === 'rejected') {
      return reject(typeof result.reason === 'string' ?
        result.reason : 'The Android AYA request was rejected.');
    }
    return reject('Unknown AYA native status. No assistant outcome is known.');
  } catch {
    return reject('AYA Android bridge failed locally. No recipient outcome is known.');
  }
}
