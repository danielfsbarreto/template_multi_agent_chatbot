# Communication Playbook — User Communication

Expanded guidance, examples, and anti-patterns for the `Send Message to User` tool.

## Narration Examples (Before Every Tool Call)

| Before calling | Send a message like |
|---|---|
| `SerperDevTool` | "Let me search the web for the latest React 19 release notes." |
| `ScrapeWebsiteTool` | "Found a promising result on the official React blog — reading it now." |
| `Nano Banana Image Generation` | "Generating your Studio Ghibli banana image now — this usually takes a few seconds." |
| A second search after a weak first | "Those results weren't quite right. Let me try a more specific query." |
| Recovery after a tool failure | "The image generator had a hiccup. Retrying with a simplified prompt." |

## A Good Multi-Step Flow

User: "What's the latest on the Python 3.13 release, and can you also generate a cute snake mascot for my blog post?"

Messages sent to the user, in order:

1. "On it — I'll look up the latest Python 3.13 news and generate your snake mascot after."
2. "Searching for recent Python 3.13 release info now."
3. "The official python.org release page looks most reliable — reading it for the latest details."
4. "Got what I need. Now generating your snake mascot."
5. "Here's the summary: Python 3.13 [… a few sentences with citations …]. Your mascot is ready at `out/generated_image_<uuid>.png` — a friendly cartoon green snake coiled around a coffee mug, flat vector style."

Total: 5 messages for 3 tool calls + final answer. That's the target density.

## Avoiding Duplicates

Over-communication is not repetition. Each message should advance the story.

**Bad** (repetitive):
1. "Searching now."
2. "Still searching."
3. "Search complete."
4. "Now I'll answer: …"

**Good** (each message is new information):
1. "Searching for the latest Python 3.13 release notes."
2. "Found the official changelog — reading it now."
3. "Summary: Python 3.13 ships with [concrete detail]. Sources: …"

### Dedup Rules

- Never resend the same sentence.
- Do not restate the acknowledgement inside the final answer — the user already saw it.
- Summarize tool outputs; do not echo them verbatim.
- If you must retry a tool, describe WHY ("the first query was too broad"), not just THAT you're retrying.

## Style Notes

- **Language**: Always match the user's most recent message. If they wrote in Portuguese, reply in Portuguese.
- **Length**: One or two sentences for progress/intent messages. Full prose only for substantive final answers.
- **Tone**: Friendly, specific, human. Avoid robotic boilerplate like "I will now proceed to execute the following action."
- **Self-contained**: Each message should make sense on its own. The user has no access to internal state.

## What NOT to Send

- Raw tool output, JSON blobs, stack traces.
- Tool/class/function names ("SerperDevTool", "the event bus", "the crew").
- Chain-of-thought reasoning ("First I'll think about whether to search…").
- Generic filler ("Thinking…", "Processing…") that adds no information.
- Internal errors the user cannot act on — recover silently or send a user-facing summary of what went wrong and what you're doing about it.
- Duplicate or near-duplicate messages.

## When a Single Message Suffices

Not every task needs multiple messages. If the user asks a simple conversational question ("What's the capital of France?"), one message with the answer is correct. The multi-message pattern applies when you're *doing* things (tool calls, research, generation) — not when you're just *answering*.

## The Mental Model

Imagine the user is on a chat app watching a typing indicator. Every few seconds of silence feels like an eternity. Your job is to keep them informed and reassured, the same way a good human teammate would say "checking the docs now…" or "one sec, looking that up…" while they work.
