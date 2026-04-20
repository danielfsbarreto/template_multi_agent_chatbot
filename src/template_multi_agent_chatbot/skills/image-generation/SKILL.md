---
name: image-generation
description: Rules for generating and editing images with the Nano Banana tools. Use the generation tool when the user asks to create a new image from scratch. Use the editing tool when the user asks to modify, alter, or transform an existing image.
metadata:
  author: template_multi_agent_chatbot
  version: "4.0"
---

## Image Generation — Core Rules

Use **`Nano Banana Image Generation`** when the user wants a brand-new image.

1. **Only use for visual creative assets.** Never for charts, plots, or data viz.
2. **Always expand the user's request into a concrete prompt** before calling the tool. A strong prompt names: subject, style, composition, lighting, color palette, and constraints. If the request is vague, either make reasonable assumptions (and mention them) or ask one focused clarifying question.
3. **Pass a single descriptive `prompt` string.** On success the tool saves the file to `out/HHMMSS.png` and returns the filename. On failure it returns a failure message — apologize briefly and offer to retry with a refined prompt.
4. **The image is automatically delivered to the user.** You do NOT need to attach, embed, or link to it yourself.
5. **After success, confirm and describe in 1–2 sentences** what you generated so the user knows what to expect alongside the image they receive.

## Image Editing — Core Rules

Use **`Nano Banana Image Editing`** when the user wants to modify an existing image.

1. **Requires a source image.** You must provide the `image_path` of a previously generated or known image (e.g. `out/140110.png`). If you don't know the path, check conversation history for a recent generation result or ask the user.
2. **Write clear edit instructions in the `prompt`.** Describe what should change (e.g. "add sunglasses to the person", "change the background to a beach at sunset", "make it look like a watercolor painting"). Be specific about what to keep and what to alter.
3. **On success the edited image is saved to `out/HHMMSS.png`** and automatically delivered to the user, just like generation.
4. **After success, briefly describe the edits** so the user knows what changed compared to the original.

## Choosing Between Generation and Editing

| User intent | Tool to use |
|---|---|
| "Create / generate / draw / make me an image of…" | Generation |
| "Edit / modify / change / add … to that image" | Editing |
| "Make it more…" / "Remove the…" / "Change the background" | Editing (on the most recent image) |
| "Try again" / "Redo it" with no existing image referenced | Generation (new attempt) |

When the user says "change it" or "edit that", use the most recently generated/edited image path from the conversation as the `image_path`.

Additional prompt-crafting detail (checklist, worked examples, anti-patterns) is available in the skill's `references/prompt-crafting.md`.
