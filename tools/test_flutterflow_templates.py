"""Limited source-contract checks; these are not editor/device integration tests."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WIDGET = ROOT / "integrations/flutter/flutterflow/aya_help_widget.dart"
ACTION = ROOT / "integrations/flutter/flutterflow/aya_open_help_action.dart"


class FlutterFlowTemplateContractTests(unittest.TestCase):
    def test_card_exposes_honest_host_copy_and_no_direct_share(self):
        data = WIDGET.read_text(encoding="utf-8")
        for field in ("description", "attachmentDisclosure", "outputInstructions"):
            self.assertIn("required this." + field, data)
        self.assertIn("AyaHelpCard(", data)
        self.assertIn("minHeight: height ?? 0", data)
        for forbidden in ("ACTION_SEND", "startActivity", "onAgentAnswered"):
            self.assertNotIn(forbidden, data)

    def test_action_reports_local_status_only(self):
        data = ACTION.read_text(encoding="utf-8")
        self.assertIn("AyaFlutter.openHelp(", data)
        self.assertIn("askQuestion: false", data)
        for status in ("question_opened", "review_opened", "rejected"):
            self.assertIn("'" + status + "'", data)
        for forbidden in ("agent_finished", "share_completed", "auto_import"):
            self.assertNotIn(forbidden, data)


if __name__ == "__main__":
    unittest.main()
