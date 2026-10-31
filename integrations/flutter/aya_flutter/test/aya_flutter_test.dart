import 'package:aya_flutter/aya_flutter.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    debugDefaultTargetPlatformOverride = TargetPlatform.android;
  });

  tearDown(() {
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(AyaFlutter.channel, null);
    debugDefaultTargetPlatformOverride = null;
  });

  test('result reports only local review opening', () async {
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(AyaFlutter.channel, (call) async {
      expect(call.method, 'openHelp');
      expect(call.arguments['guideAsset'], 'aya-guide.md');
      return {'status': 'review_opened'};
    });
    final response = await AyaFlutter.openHelp(question: 'example');
    expect(response.status, AyaLocalStatus.reviewOpened);
    expect(response.rejected, isFalse);
  });

  test('unknown native states reject instead of claiming success', () async {
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(AyaFlutter.channel, (call) async {
      return {'status': 'agent_finished'};
    });
    final response = await AyaFlutter.openHelp(question: 'example');
    expect(response.status, AyaLocalStatus.rejected);
  });

  test('invalid asset is rejected before native dispatch', () async {
    final response = await AyaFlutter.openHelp(guideAsset: '../guide.md');
    expect(response.rejected, isTrue);
  });

  testWidgets('host card discloses output path and only sends on user tap',
      (tester) async {
    var calls = 0;
    String? question;
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(AyaFlutter.channel, (call) async {
      calls++;
      question = call.arguments['question'] as String?;
      return {'status': 'review_opened'};
    });
    await tester.pumpWidget(const MaterialApp(
      home: Scaffold(
        body: SingleChildScrollView(
          child: AyaHelpCard(
            description: 'How to use this app.',
            attachmentDisclosure: 'A guide may be offered as text.',
            outputInstructions: 'Follow the instructions manually.',
          ),
        ),
      ),
    ));
    expect(find.textContaining('Follow the instructions manually.'), findsOneWidget);
    expect(calls, 0);
    await tester.enterText(find.byType(TextField), 'What is this screen?');
    await tester.tap(find.text('Ask Your Agent'));
    await tester.pumpAndSettle();
    expect(calls, 1);
    expect(question, 'What is this screen?');
  });
}
