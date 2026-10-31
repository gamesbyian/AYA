import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Local host results only. No third-party assistant result is ever observed.
enum AyaLocalStatus { questionOpened, reviewOpened, rejected }

@immutable
class AyaLocalResult {
  const AyaLocalResult(this.status, {this.reason});
  final AyaLocalStatus status;
  final String? reason;
  bool get rejected => status == AyaLocalStatus.rejected;
}

/// Android bridge using the installed-version-checked AYA native Help action.
class AyaFlutter {
  const AyaFlutter._();

  @visibleForTesting
  static const MethodChannel channel = MethodChannel('dev.aya/flutter_handoff');

  static Future<AyaLocalResult> openHelp({
    String guideAsset = 'aya-guide.md',
    String? screenName,
    String question = '',
    bool askQuestion = false,
  }) async {
    if (defaultTargetPlatform != TargetPlatform.android) {
      return const AyaLocalResult(AyaLocalStatus.rejected,
          reason: 'AYA handoff is available in Android builds only.');
    }
    if (guideAsset.trim().isEmpty || guideAsset.startsWith('/') ||
        guideAsset.split('/').contains('..') || guideAsset.contains(r'\')) {
      return const AyaLocalResult(AyaLocalStatus.rejected,
          reason: 'Invalid guide asset path.');
    }
    try {
      final result = await channel.invokeMapMethod<String, dynamic>(
        'openHelp',
        <String, Object?>{
          'guideAsset': guideAsset,
          'screenName': screenName,
          'question': question,
          'askQuestion': askQuestion,
        },
      );
      switch (result?['status']) {
        case 'question_opened':
          return const AyaLocalResult(AyaLocalStatus.questionOpened);
        case 'review_opened':
          return const AyaLocalResult(AyaLocalStatus.reviewOpened);
        case 'rejected':
          return AyaLocalResult(AyaLocalStatus.rejected,
              reason: result?['reason']?.toString() ?? 'Local AYA request rejected.');
        default:
          return const AyaLocalResult(AyaLocalStatus.rejected,
              reason: 'Unexpected response from the local AYA Android bridge.');
      }
    } on PlatformException catch (error) {
      return AyaLocalResult(AyaLocalStatus.rejected,
          reason: error.message ?? 'The Android AYA bridge is unavailable.');
    } on MissingPluginException {
      return const AyaLocalResult(AyaLocalStatus.rejected,
          reason: 'AYA Android bridge is not installed in this build.');
    }
  }
}

/// Host-themed card. The host supplies real app-specific description and
/// return-use instructions. This never transmits before explicit user review.
class AyaHelpCard extends StatefulWidget {
  const AyaHelpCard({
    super.key,
    required this.description,
    required this.attachmentDisclosure,
    required this.outputInstructions,
    this.title = 'Ask Your Agent',
    this.guideAsset = 'aya-guide.md',
    this.screenName,
    this.questionHint = 'What would you like help with? (optional)',
    this.initialQuestion = '',
    this.restorationId,
    this.onLocalResult,
  }) : assert(outputInstructions.length > 0);

  final String title;
  final String description;
  final String attachmentDisclosure;
  final String outputInstructions;
  final String guideAsset;
  final String? screenName;
  final String questionHint;
  final String initialQuestion;
  final String? restorationId;
  final ValueChanged<AyaLocalResult>? onLocalResult;

  @override
  State<AyaHelpCard> createState() => _AyaHelpCardState();
}

class _AyaHelpCardState extends State<AyaHelpCard> with RestorationMixin {
  late final RestorableTextEditingController _question;
  bool _busy = false;

  @override
  void initState() {
    super.initState();
    _question = RestorableTextEditingController(text: widget.initialQuestion);
  }

  @override
  String? get restorationId => widget.restorationId;

  @override
  void restoreState(RestorationBucket? oldBucket, bool initialRestore) {
    registerForRestoration(_question, 'question');
  }

  Future<void> _openReview() async {
    if (_busy) return;
    setState(() => _busy = true);
    final local = await AyaFlutter.openHelp(
      guideAsset: widget.guideAsset,
      screenName: widget.screenName,
      question: _question.value.text,
      askQuestion: false,
    );
    if (!mounted) return;
    setState(() => _busy = false);
    widget.onLocalResult?.call(local);
    if (local.rejected) {
      ScaffoldMessenger.maybeOf(context)?.showSnackBar(SnackBar(
          content: Text(local.reason ?? 'AYA is unavailable in this build.')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: theme.colorScheme.outline),
        borderRadius: BorderRadius.circular(12),
      ),
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(widget.title, style: theme.textTheme.titleMedium),
          const SizedBox(height: 6),
          Text(widget.description),
          const SizedBox(height: 8),
          Text(widget.attachmentDisclosure, style: theme.textTheme.bodySmall),
          const SizedBox(height: 6),
          Text('After your agent replies: ' + widget.outputInstructions,
              style: theme.textTheme.bodySmall),
          const SizedBox(height: 8),
          TextField(
            controller: _question.value,
            decoration: InputDecoration(
              labelText: widget.questionHint,
              border: const OutlineInputBorder(),
            ),
            keyboardType: TextInputType.multiline,
            minLines: 1,
            maxLines: null,
          ),
          const SizedBox(height: 8),
          SizedBox(
            height: 48,
            child: FilledButton(
              onPressed: _busy ? null : _openReview,
              child: const Text('Ask Your Agent'),
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _question.dispose();
    super.dispose();
  }
}
