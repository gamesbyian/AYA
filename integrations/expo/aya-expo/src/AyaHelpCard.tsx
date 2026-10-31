import React, { useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  useColorScheme,
  View
} from 'react-native';
import { openAyaHelp } from './native';
import type { AyaLocalResult } from './index';

export type AyaHelpCardProps = {
  description: string;
  attachmentDisclosure: string;
  outputInstructions: string;
  title?: string;
  guideAsset?: string;
  screenName?: string;
  questionHint?: string;
  initialQuestion?: string;
  onLocalResult?: (result: AyaLocalResult) => void;
};

/**
 * A real visible native RN control; never accesses user files or AI replies.
 * Its host controls layout/scrolling; it makes no network calls.
 */
export function AyaHelpCard(props: AyaHelpCardProps) {
  const [question, setQuestion] = useState(props.initialQuestion ?? '');
  const [busy, setBusy] = useState(false);
  const [failure, setFailure] = useState<string | null>(null);
  const dark = useColorScheme() === 'dark';
  const ink = dark ? '#ffffff' : '#202124';
  const border = dark ? '#909090' : '#777777';
  const valid = Boolean(
    props.description?.trim() &&
    props.attachmentDisclosure?.trim() &&
    props.outputInstructions?.trim()
  );

  if (!valid) {
    return (
      <Text accessibilityRole="alert" style={{ color: ink }}>
        AYA unavailable: the host must describe the guide and how to use the answer.
      </Text>
    );
  }

  const ask = async () => {
    if (busy) return;
    setBusy(true);
    setFailure(null);
    try {
      const result = await openAyaHelp({
        question, guideAsset: props.guideAsset,
        screenName: props.screenName, askQuestion: false
      });
      props.onLocalResult?.(result);
      if (result.status === 'rejected') {
        setFailure(result.reason ?? 'AYA local review unavailable.');
      }
    } finally {
      setBusy(false);
    }
  };

  return (
    <View style={[styles.card, { borderColor: border }]}
          accessibilityLabel="Ask Your Agent help card">
      <Text style={[styles.title, { color: ink }]}>
        {props.title ?? 'Ask Your Agent'}
      </Text>
      <Text style={{ color: ink }}>{props.description}</Text>
      <Text style={{ color: ink }}>{props.attachmentDisclosure}</Text>
      <Text style={{ color: ink }}>
        After your agent replies: {props.outputInstructions}
      </Text>
      <TextInput
        multiline
        placeholder={props.questionHint ?? 'Question for your agent (optional)'}
        accessibilityLabel="Question for your agent, optional"
        onChangeText={setQuestion}
        value={question}
        style={[styles.question, { borderColor: border, color: ink }]}
        placeholderTextColor={dark ? '#aaaaaa' : '#555555'}
        textAlignVertical="top"
      />
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Review your question and app guide before sharing"
        disabled={busy}
        onPress={() => { void ask(); }}
        style={[styles.action, { backgroundColor: dark ? '#ffffff' : '#202124' }]}
      >
        {busy ? <ActivityIndicator color={dark ? '#202124' : '#ffffff'} /> :
          <Text style={{ color: dark ? '#202124' : '#ffffff', fontWeight: '600' }}>
            Ask Your Agent
          </Text>}
      </Pressable>
      {failure && <Text accessibilityRole="alert" style={{ color: ink }}>{failure}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  card: { borderWidth: 1, borderRadius: 12, padding: 12, gap: 8 },
  title: { fontSize: 18, fontWeight: '700' },
  question: { borderWidth: 1, borderRadius: 8, padding: 12, minHeight: 72, fontSize: 16 },
  action: {
    minHeight: 48, borderRadius: 8,
    alignItems: 'center', justifyContent: 'center', paddingHorizontal: 16
  },
});
