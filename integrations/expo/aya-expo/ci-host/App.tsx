import React from 'react';
import { SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';
import { AyaHelpCard } from 'aya-expo';

/**
 * This single-screen Android test host is intentionally small and self-contained.
 * Its exact-version AYA-RAS reference documents only the UI and code below.
 */
export default function App() {
  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.heading}>AYA Expo CI Host</Text>
        <Text style={styles.note}>A test application for reviewed Android help handoffs.</Text>
        <View style={styles.card}>
          <AyaHelpCard
            description="Ask about this test host's one-screen help interface."
            attachmentDisclosure="An app guide is offered as a text attachment. Your AI app may ignore attachments."
            outputInstructions="Read the response and apply advice manually. This host cannot import or execute agent outputs."
            screenName="Expo CI host"
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#ffffff' },
  content: { padding: 16, gap: 12 },
  heading: { color: '#202124', fontSize: 22, fontWeight: '700' },
  note: { color: '#202124', fontSize: 16 },
  card: { maxWidth: 640 },
});
