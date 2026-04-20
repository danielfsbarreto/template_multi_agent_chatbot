---
name: internet-searching
description: Rules for searching the web and scraping pages using SerperDevTool and ScrapeWebsiteTool. Use when the user asks about current events, recent docs/data, specific URLs, or facts that may have changed since training.
metadata:
  author: template_multi_agent_chatbot
  version: "2.0"
---

## Internet Searching — Core Rules

You have two web tools:

- **`Search the internet with Serper`** — Google search, returns snippets with URLs.
- **`Read website content`** — fetches the readable content of a single URL.

### Workflow

1. **Rewrite** the user's request into a focused keyword query (include product names, versions, the current year if freshness matters).
2. **Search first** with Serper. Scan snippets for authoritative, recent results.
3. **Scrape only when snippets are insufficient.** Pick 1–3 of the most promising URLs (prefer official/primary sources) and fetch them.
4. **Synthesize** across sources. Note disagreements rather than picking one at random.
5. **Always include sources.** Every answer that uses web information MUST end with a list of the URLs you consulted. No exceptions.

### Citations Are Mandatory

Any time you search or scrape, your final message to the user **must** include the reference links. Format them as a short list at the end of your answer:

- Source title or short description — URL

If you consulted multiple pages, list every one you actually drew information from. Never omit sources, and never fabricate a URL you didn't visit.

### Non-Negotiables

- **Do not search** when the answer is stable general knowledge, the question is purely conversational, or the user asked you not to use external sources.
- **Do not scrape** a page you don't intend to read — each call costs latency and quota.
- **Do not fabricate citations.** Only cite URLs you genuinely consulted.
- **If a query returns weak results, reformulate it** — don't repeat the same query.

Additional query-crafting techniques, source-quality ranking, and scraping tips are available in the skill's `references/search-techniques.md`.
