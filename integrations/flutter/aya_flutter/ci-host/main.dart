import 'package:aya_flutter/aya_flutter.dart';
import 'package:flutter/material.dart';

void main() => runApp(const AyaFlutterCiHost());

/// Build-only evidence host. The AYA Android bridge still requires an actual
/// Activity and the exact-version aya-guide.md packaged in Android APK assets.
class AyaFlutterCiHost extends StatelessWidget {
  const AyaFlutterCiHost({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AYA Flutter CI Host',
      home: Scaffold(
        appBar: AppBar(title: const Text('AYA Flutter CI Host')),
        body: const SafeArea(
          child: SingleChildScrollView(
            padding: EdgeInsets.all(16),
            child: AyaHelpCard(
              title: 'Ask Your Agent',
              description: 'Ask how the AYA Flutter test host works.',
              attachmentDisclosure:
                  'This test-host reference is offered as a text attachment. '
                  'Your receiving AI app might not accept files.',
              outputInstructions:
                  'Read the answer and apply any useful advice yourself. '
                  'This CI host does not import or apply agent replies.',
              screenName: 'Flutter CI host',
            ),
          ),
        ),
      ),
    );
  }
}
