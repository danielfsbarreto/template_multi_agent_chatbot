---
name: image-generation
description: Rules for generating images with the Nano Banana Image Generation tool. Use when the user asks to create, draw, illustrate, render, or visualize an image (logos, icons, mockups, concept art, wallpapers). Not for charts, plots, or data visualizations.
metadata:
  author: template_multi_agent_chatbot
  version: "3.0"
---

## Image Generation — Core Rules

1. **Only use for visual creative assets.** Never for charts, plots, data viz, or editing existing images.
2. **Always expand the user's request into a concrete prompt** before calling the tool. A strong prompt names: subject, style, composition, lighting, color palette, and constraints. If the request is vague, either make reasonable assumptions (and mention them) or ask one focused clarifying question.
3. **Pass a single descriptive `prompt` string** to the tool. On success it returns `"Image generated successfully."` and saves the file to `out/HHMMSS.png` (UTC timestamp). On failure it returns `"Failed to generate image."` — apologize briefly and offer to retry with a refined prompt.
4. **The image is automatically delivered to the user.** On success the tool emits an event that sends the generated image directly to the user. You do NOT need to attach, embed, or link to the image yourself.
5. **After success, confirm and describe in 1–2 sentences** what you generated so the user knows what to expect alongside the image they receive.

Additional prompt-crafting detail (checklist, worked examples, anti-patterns) is available in the skill's `references/prompt-crafting.md`.
