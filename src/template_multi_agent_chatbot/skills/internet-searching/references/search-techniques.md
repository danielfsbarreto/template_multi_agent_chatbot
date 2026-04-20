# Search Techniques Reference — Internet Searching

Advanced tips for getting high-quality results out of `SerperDevTool` and `ScrapeWebsiteTool`.

## Query Crafting

### Freshness

- Include the current year for time-sensitive topics: `"best Python web framework 2026"`.
- Add words like `latest`, `release notes`, `changelog`, `as of`, or a specific month when freshness matters.
- For breaking news, include `news` or the publication name.

### Precision

- **Quote exact phrases** to force literal matching: `"progressive disclosure"`.
- **Combine quoted phrase + keyword** for focused results: `"skill activation" crewai`.
- **Exclude noise** with `-term` (Google operator): `python async -asyncio`.

### Site Scoping

- `site:docs.crewai.com skills` — restricts results to one domain.
- `site:github.com crewAIInc` — good for finding repos, issues, PRs.
- Stack with quotes: `"SerperDevTool" site:docs.crewai.com`.

### Disambiguation

- Add the domain/context when a term is ambiguous: `Jaguar animal` vs `Jaguar car` vs `Jaguar F1`.
- Include the technology stack: `"pagination" postgres` vs `"pagination" react`.

### Retry Strategy

If the first search is weak:

1. **Reformulate** with different keywords — don't just retry the same query.
2. **Add constraints** (year, site, quotes) to narrow, or remove them to broaden.
3. **Try a related angle** — e.g. search for the error message instead of the concept, or the official doc instead of a blog.

## Source Quality Ranking

Prefer sources in this order:

1. **Primary / official** — Vendor docs, original repos, official changelogs, first-party announcements.
2. **Reputable publications** — Established tech/news outlets with editorial standards.
3. **Recognized expert blogs** — Well-known practitioners writing in their area of expertise, ideally recent.
4. **Community Q&A** — Stack Overflow, GitHub issues/discussions. Useful for edge cases, but verify against primary sources.

Be skeptical of:

- Content farms and SEO-optimized listicles with no author.
- Undated pages, especially for fast-moving topics.
- Pages that contradict primary sources.
- AI-generated content farms (watch for generic phrasing, no original insight).

## Scraping Tips

- Scrape the **most authoritative URL first**, then a secondary source only if you need to cross-check.
- If a scrape returns obviously broken content (paywall stub, JS-only page, cookie wall), acknowledge it and try a different URL — don't fabricate detail from a bad scrape.
- Prefer `docs.*` subdomains over blog posts when both cover the same topic.

## Responding with Citations

- Give the direct answer first, then supporting detail, then citations.
- Citation format: short title + URL. One per distinct source actually used.
- If sources disagree, state the disagreement and which source you're trusting and why.
- If you couldn't verify something, say so — don't guess.

## Cost Awareness

- One well-crafted search beats three shallow ones.
- Only scrape pages you will actually read and cite.
- For very broad research, prefer a single specific search over many variations.
