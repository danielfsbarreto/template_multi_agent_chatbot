# Prompt Crafting Reference — Image Generation

Use this checklist when turning a user request into a prompt for the `Nano Banana Image Generation` tool.

## The Six Ingredients

A strong prompt names each of the following. Omit an ingredient only if the user has already constrained it.

1. **Subject** — The main focus.
   - e.g. "a red panda", "a futuristic city skyline", "a minimalist coffee cup logo"
2. **Style / Medium** — The visual language.
   - e.g. "flat vector illustration", "photorealistic", "watercolor", "3D isometric render", "Studio Ghibli anime style", "pixel art"
3. **Composition** — Framing and layout.
   - e.g. "close-up portrait", "wide establishing shot", "centered", "rule-of-thirds", "isometric top-down"
4. **Lighting & Mood** — The emotional tone.
   - e.g. "soft morning light", "dramatic cinematic lighting", "neon cyberpunk glow", "overcast and moody"
5. **Color Palette** — The color story.
   - e.g. "muted earth tones", "vibrant pastels", "monochrome blue", "warm brown and cream"
6. **Constraints** — Explicit inclusions or exclusions.
   - e.g. "no text", "transparent background", "clean lines", "high detail", "minimal"

## Worked Examples

### Example 1 — Logo

User: "Can you make me a logo for a coffee shop called 'Bean There'?"

Prompt:
> Minimalist flat vector logo for a coffee shop named "Bean There". A stylized coffee bean forming the letter "B", warm brown and cream color palette, centered composition, clean lines, transparent background, no extra text.

### Example 2 — Character

User: "Draw a wizard cat"

Prompt:
> Whimsical digital illustration of a wise old cat wearing a purple wizard robe and pointed hat, holding a glowing wooden staff. Studio Ghibli anime style, soft warm lighting, centered medium shot, muted jewel-tone palette, detailed fur texture, no text.

### Example 3 — Scene

User: "I want a wallpaper of a mountain lake at sunrise"

Prompt:
> Photorealistic wide landscape of a glassy alpine lake at sunrise, snow-capped mountains mirrored on the water, pine trees in the foreground, soft golden-pink lighting, serene and tranquil mood, 16:9 aspect ratio, high detail, no text or watermarks.

## When the Request Is Vague

If the user says only "make me an image of a cat", pick reasonable defaults across the six ingredients (e.g. photorealistic, centered medium shot, natural lighting, neutral palette) and briefly mention those choices when you deliver the result, so the user can refine if they want.

If a key decision point is truly ambiguous (e.g. style: cartoon vs photorealistic), ask ONE focused question before generating.

## Anti-Patterns

- Passing the user's raw request as the prompt (e.g. "draw a cat" → too little signal).
- Specifying contradictory styles (e.g. "photorealistic watercolor pixel art").
- Requesting embedded text — text rendering is unreliable; prefer "no text" unless text is essential, and keep any required text short.
- Long prose; favor dense noun/adjective phrases.
