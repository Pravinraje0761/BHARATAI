# AI Teacher — Refinement Pass (review of current docs)

*This is a review of the documentation text you pasted, not the code itself — I don't have your repo. If you want a real code-level pass (checking the implementation actually matches what the docs claim), share the repo or connect the folder and I'll go through it directly. Everything below is prioritized by rubric impact, cheapest-first within each tier.*

## Critical — check this before anything else

**Follow-up questions aren't in your architecture, and Task 2 names them explicitly.**
Section 11's Task 2 mandatory list includes *"Answer follow-up questions while maintaining lesson context"* — that's a distinct capability from your `EXPLAIN → QUESTION → EVALUATE → ADAPT` loop, which only handles teacher-initiated checkpoint questions. As documented, there's no path for the *student* to interrupt with their own question ("wait, why does resistance affect current at all?") and get an answer grounded in the current segment/lesson state.

This is cheap to add given what you already have: a `FOLLOWUP` handler that takes free-text student input at any point, answers it using the current segment's retrieved context + lesson-plan state (same grounding machinery you already built for `EXPLAIN`), and returns to wherever the state machine was before the interruption. Since your RAG and prompt infrastructure already exists, this is mostly wiring, not new capability — but it closes a named mandatory gap, so it should jump the queue over everything else here.

## High ROI, low additional risk

**1. Subject-aware visuals are currently one template, but Section 10 is graded on differentiation.**
"Subject-tinted slide" (color + bullets) is one visual type with a palette swap, not different *representations* per subject. The brief is explicit: math wants equations/graphs, physics wants diagrams/processes, biology wants labeled diagrams, history wants timelines, programming wants code/execution flow — and it separately warns that a generic slide behind an avatar won't be judged sufficient. Given this is worth 15% on its own line, it's worth the highest remaining build effort:
- Add a lightweight subject/visual-type classifier (an LLM call or simple keyword rule) per segment that picks from: `equation/graph` (render with matplotlib), `code block` (syntax-highlighted, for programming segments), `timeline` (PIL, for history), `labeled diagram` (even a simple annotated shape diagram beats another bullet slide), falling back to your current bullet slide for anything else.
- Document *how* the classifier decides — the brief asks you to show your reasoning here, not just produce the visuals.

**2. Concept maps + auto-notes are nearly free, given data you already collect.**
Your lesson plan already has ordered concepts with relationships, and your teaching log already has full explanation text per segment. Two Section 18 advanced features fall out of that with almost no new AI work:
- **Concept map**: a graphviz render of the segment concepts as nodes with prerequisite/related edges (you likely already have or can trivially infer the ordering).
- **Auto-notes / flashcards**: reformat the taught explanations + examples into a study sheet or Q/A flashcard set at lesson end — pure formatting over data you already have.
Both are Innovation/Originality (5%) and Advanced Features credit for maybe an hour of work each, since no new model calls are required.

**3. Question-type variety.**
Section 11 lists six interaction types; you're alternating two (MCQ/short-answer). Adding "explain in your own words" as a third rotation is especially valuable — it's the hardest to game and the most convincing demonstration of real understanding-checking to a jury, and your grader already handles free-text evaluation, so it's config, not new code.

**4. Close the personalization loop across sessions.**
Right now `recommend_next_topic` produces a suggestion but doesn't feed back into *how* the next lesson is planned. Passing the student's weak/strong concept history into the lesson-plan agent for their next session (so it starts already adjusted — e.g. spends more time on a previously-weak prerequisite) turns your profile store from a report generator into something that visibly changes future behavior, which is what Section 14 ("The AI should use this information to personalize future teaching sessions") is actually asking for.

## Cheap polish

- **Avatar liveliness**: a 4th mouth frame for occasional blinking, plus a 1–2px vertical idle bob, reads as noticeably more "alive" on video for very little effort — worth it since Voice/Avatar is a full 10% line and yours is intentionally the simplest part of the pipeline.
- **Cross-language material test**: the brief explicitly calls out "English textbook → Hindi teaching" and the reverse as a scenario. Confirm you've actually tested ingesting a non-English document and teaching it in a different language, and say so in the docs — right now the doc only confirms multilingual *generation*, not that ingestion is language-agnostic.
- **Report format**: their example shows a percentage ("Score: 80%"); you're emitting `"X/Y"`. Emit both — trivial change, closer match to what they asked for.
- **Scanned/OCR PDFs**: your earlier plan mentioned a Tesseract fallback for scanned material; the current ingestion writeup doesn't mention it. Either confirm it's in there, or explicitly add it to known limitations rather than leaving it silently unaddressed.
- **Architecture diagram**: your ASCII pipeline diagram is genuinely good and correct — for the final submission packet, consider rendering a proper visual version too (even a simple boxes-and-arrows image). Documentation is only 5% but it's a jury-attention-cheap way to look more finished.

## What NOT to touch

Your teaching state machine (few-shot misconception grading, different-analogy re-explanation, depth bump on streak) and your citation-grounded RAG are the strongest parts of this submission and match exactly what the rubric weights heaviest (35% combined). Don't spend more time refining these unless you find an actual bug — spend remaining time on the follow-up-question gap and the subject-aware visuals instead, since those are the two places where your documentation shows real distance between what's built and what's explicitly asked for.
