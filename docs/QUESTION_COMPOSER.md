# Question-first AYA UX contract

An app's Help action should be a natural continuation of what the user is doing, not a demand to understand files or AI import formats.

## Default journey

1. User taps **Ask your agent** from the host app.
2. AYA shows a compact, keyboard-friendly **What do you need help with?** question field. The app may prefill a relevant suggestion; the user can freely rewrite or leave it blank for general help.
3. User taps **Review details**. AYA composes the question, installed version, screen hint, and bundled AYA-RAS reference into a single self-contained help package.
4. AYA shows the full editable disclosure preview; the user can Cancel, Copy, or Share. The preview explains that the destination may store/upload the content, and Android may expose the question as separate message text.
5. Android Sharesheet opens with one text attachment and, if available, the **final approved** question as `EXTRA_TEXT`. The user picks a receiver. Chat creation, attachment ingestion and final sending are up to it.
6. The user may use Copy and manual paste if the receiver fails to import the file.

This is a *two-stage consent flow*: writing a question does not send it, and preview/editing does not imply that an AI provider has received anything.

## Integration patterns

**Standard question-first**: `Aya.launchBundled(activity, screenName="Connections")`. `askQuestion=true` is the default.

**Host already has a question field**: `Aya.launchBundled(activity, question=userTypedText, askQuestion=false)`. This goes straight to the **privacy preview**, avoiding an unnecessary second question box. The host must preserve the user's exact question and avoid adding private data without review.

**Prefill a suggestion but allow editing**: `Aya.launchBundled(activity, question="How do I configure this screen?")`, using the default `askQuestion=true`.

**Low-level/manual request**: `Aya.ask(activity, AyaRequest(...))` opens the question composer with explicitly supplied guide content. `Aya.launch(activity, AyaRequest(...))` retains the original direct-to-preview behavior.

## UX and accessibility criteria

- Use large multiline input, natural hint, explicit 'question optional' labeling, standard Android keyboard and back behavior.
- Preserve user input through the transition from question to preview. Ensure that editing/removing text in preview changes both the attachment and separate shared question.
- Support empty questions with a generic support request; don't force users to invent a question just to learn an app.
- Do not require the user to select an assistant before entering the question. Android's chooser handles recipient selection.
- Keep a distinct final **Share** action separate from **Review details**, never silently send because the user pressed Continue.
- Avoid implicit diagnostic collection: screens and questions are supplied by host or user, never scraped from elsewhere.
- Human acceptance: TalkBack labels, 320x700/412x892 portrait, rotation/Activity recreation, font scaling, keyboard overlap and repeated cancel/reopen.
- Preview of the entire guide can be lengthy. Future polish may offer collapsible sections and a concise disclosure summary without hiding what will be shared.

## Observable tests

1. Blank question proceeds using a generic question in document.
2. User-edited prefilled question replaces host suggestion.
3. Multiline questions survive without data loss.
4. Editing/removing question in review does not leak previous content in `EXTRA_TEXT`.
5. A very large question is present fully in attachment, but message extra stays bounded.
6. Cancel from either dialog results in no new share intent.
7. A receiver that ignores file still sees question (when it accepts `EXTRA_TEXT`).
8. A receiver that ignores `EXTRA_TEXT` can answer from the attached package (when it accepts file).

The last two require receiver-specific device tests rather than ordinary Kotlin unit tests.
