# Acceptance plan

**Unexecuted.**

Automated: document rendering tests (required fields, optional fields, guide text); Android instrumentation (readable URI with grant, denied without grant, chooser success/failure, lifecycle and long payloads); inspect merged manifest and lack of networking permissions.

Manual devices: Android 10, 13, 15, 16+; ChatGPT and Claude installed/logged-in and logged-out, plus generic text targets. Record destination app version and test date, availability in sharesheet, attachment ingestion, prompt visibility, whether new chat starts, and whether user needs to press Send. Test font scaling, TalkBack, 320x700 and 412x892 screens, keyboard and landscape.

Release gate: successful Gradle build, integrated demo application, accessible review UI, tested cache retention/cleanup and no claims of provider support beyond observed versions.
