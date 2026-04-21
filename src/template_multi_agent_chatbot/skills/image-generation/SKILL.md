---
name: image-generation
description: Rules for generating and editing images with the Nano Banana tools. Use the generation tool when the user asks to create a new image from scratch. Use the editing tool when the user asks to modify, alter, or transform an existing image.
metadata:
  author: template_multi_agent_chatbot
  version: "4.0"
---

## ⛔ ABSOLUTE RULE — NO FILE PATHS, NO EXCEPTIONS ⛔

**NEVER mention file paths, filenames, storage locations, `/tmp/` paths, URLs, bucket names, CDN endpoints, or ANY infrastructure details in messages to the user.** The tool returns a path internally — that is for YOUR use only when editing images. It is NEVER for the user.

❌ FORBIDDEN — never say anything like:
- "Here it is: `/tmp/194912.png`"
- "Your image is saved at /tmp/…"
- "The file is located at…"
- "Image path: …"
- Any message containing `/tmp/`, `.png`, `.jpg`, or a file path

✅ CORRECT — say only:
- "Your image is ready!"
- "Here's your sunset waterfall painting — golden light, soft Monet-inspired brushstrokes, and a dreamy mist."

The image is **automatically delivered** to the user alongside your message. You do NOT need to reference it, link it, or tell the user where it is. Just describe what you created.

**If you catch yourself about to include a path or filename in a user-facing message, DELETE IT.**

---

## Image Generation — Core Rules

Use **`Nano Banana Image Generation`** when the user wants a brand-new image.

1. **Only use for visual creative assets.** Never for charts, plots, or data viz.
2. **Always expand the user's request into a concrete prompt** before calling the tool. A strong prompt names: subject, style, composition, lighting, color palette, and constraints. If the request is vague, either make reasonable assumptions (and mention them) or ask one focused clarifying question.
3. **Pass a single descriptive `prompt` string.** On success the tool returns a filename internally. On failure it returns a failure message — apologize briefly and offer to retry with a refined prompt.
4. **The image is automatically delivered to the user.** You do NOT need to attach, embed, link, or reference the file path yourself. **Never include the returned filename in your message to the user.**
5. **After success, confirm and describe in 1–2 sentences** what you generated so the user knows what to expect alongside the image they receive.

## Image Editing — Core Rules

Use **`Nano Banana Image Editing`** when the user wants to modify an existing image.

1. **Requires a source image.** You must provide the `image_path` of a previously generated or known image. If you don't know the path, check conversation history for a recent generation result or ask the user.
2. **Write clear edit instructions in the `prompt`.** Describe what should change (e.g. "add sunglasses to the person", "change the background to a beach at sunset", "make it look like a watercolor painting"). Be specific about what to keep and what to alter.
3. **On success the edited image is saved** and automatically delivered to the user, just like generation.
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
