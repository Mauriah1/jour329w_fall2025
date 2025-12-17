# How To: Build a Reporter’s Beat Book with Claude (Eastern Shore Race & Diversity)

This guide distills the end‑to‑end process from the Beat Book work into a concise, repeatable workflow using Anthropic Claude. It emphasizes a no‑fabrication policy, county‑first structure, and a two‑pass (extract → synthesize) method that consistently produced the strongest results.

---

## 1) Goals & Outputs
- Create a narrative, journalist‑usable beat guide from local news coverage.
- Prioritize local sources and county context over generic advice.
- Mark high‑priority sources (appearing 3+ times) and explain why they matter.
- Produce two flavors as needed:
  - Narrative Reporter’s Guide (mentorship tone, county‑by‑county)
  - Calendar/Quick‑reference (events, recurring opportunities, contacts)

Primary outputs
- `beat_guide.md` (narrative, county‑by‑county with tips)

---

## 2) Prerequisites
- Stories JSON: a unified file such as `source_stories_final.json` (titles, dates, URLs, text/summaries).
- Optional reference doc: `important_people_organizations.md` (people/orgs mentioned ≥3 times + why important).
- Claude access (choose the method you prefer but only ensure this model can be used):
  - Option A: Anthropic Python SDK
  - Option B: Groq Open Models 

Environment suggestions
- Keep runs versioned by date/model, e.g., `beat_guide_sonnet_v1.md`.
- Save your exact prompts alongside outputs for reproducibility.

---

## 3) Data Hygiene & Guardrails
- Only use content explicitly present in your stories. No fabrication.
- If in doubt, omit rather than infer.
- Prefer local activists, organizers, residents, and county officials over state‑level voices unless the stories emphasize them.
- Use the reference doc to flag/highlight repeat sources; do not introduce new names.

Quick checks before you run
- Dates in range (e.g., 2024–2025) and valid.
- URLs present where possible for citations.
- Text fields normalized (`content` or `text`).

---

## 4) Two‑Pass Method (Claude)
Two‑pass avoids long‑context drift and preserves accuracy.

Pass 1 — Extract per batch
- Chunk your stories (e.g., batches of 25–50) within model token limits.
- Extract only essentials:
  - County/town mentions and geography
  - Events by date/location (chronological)
  - People and orgs (with counts if feasible)
  - Themes/keywords/frames used by the stories
  - Explicit quotes, titles, URLs when available
- If you have the reference doc, paste a short excerpt and instruct Claude to mark items in the batch that match the reference as HIGH PRIORITY.

Pass 2 — Synthesize
- Merge batch summaries, deduplicate, and organize by county.
- Preserve HIGH PRIORITY markers and counts.
- Order events chronologically per county.
- Keep a clear “no new facts” reminder.

---

## 5) Prompt Blueprints (Copy/Paste)

A) Extraction (per batch)

System (optional)
- “You are a careful research assistant. Only extract information explicitly present in the provided stories. Do not fabricate or infer.”

User
- “Analyze these N stories about Maryland’s Eastern Shore (Race & Diversity). Extract only explicit details.

Rules
- NO fabrication. If not present, omit it.
- Prefer local/community sources.
- If provided, treat reference list items as HIGH PRIORITY.

Output format
- COUNTIES & DEMOGRAPHICS (observed mentions; 1–2 lines)
- THEMES BY COUNTY (2–3 sentences per county)
- COMMUNITY SOURCES (Name – role/org – county; note HIGH PRIORITY; rough mention counts if observable)
- ORGANIZATIONS (Name – what they do – county; note HIGH PRIORITY)
- EVENTS BY LOCATION (County/Town – Date – What happened; chronological)
- KEYWORDS/FRAMING (repeated words/phrases)
- STORY REFERENCES (titles and/or URLs where present)
- COVERAGE PATTERNS (2–3 sentences: voices, balance, local vs. state)

Stories (verbatim):
[PASTE batch stories as plain text with Title/Date/URL/Text]
”

B) Synthesis (combine batches)

User
- “Consolidate these batch summaries. Do NOT add new facts.

Keep
- COUNTY focus (issues, events, sources)
- HIGH PRIORITY markers and mention counts
- Chronological order for events
- Local terms only (no generic jargon)

Produce
- County‑by‑county sections (3–4 paragraphs each)
- Cross‑county themes (3–4 paragraphs)
- ‘How stories get written here’ (sourcing and structure patterns)
- ‘Building your beat’ (practical reporter playbook)
- 3–5 story pitches with who to call first and what records to request
- Short glossary (local terms only)
”

C) Narrative Reporter’s Guide (final shaping)

User
- “Rewrite this consolidated material as a mentorship‑tone reporter’s guide for a newcomer to the Eastern Shore. Organize as:
  1) Understanding the Beat (2–3 paragraphs)
  2) The Players You’ll Get to Know (3–4 paragraphs; ⭐ for HIGH PRIORITY)
  3) How Stories Get Written Here (3–4 paragraphs; quotes order, frames)
  4) Building Your Beat (3–4 paragraphs; calendars, meetings, records)
  5) County‑by‑County Breakdown (3–4 paragraphs per county; chronological events; ⭐ sources; county‑specific tips)
  6) Stories Waiting to Be Told (3–5 narrative pitches)
  7) Themes Across Counties (3–4 paragraphs)
  8) Story Arcs (timeline highlights)
  9) Glossary (local terms only)
  10) Coverage Gaps & Opportunities (brief)
Do not introduce anything not present in the consolidated summary.”

D) Calendar/Quick‑Reference (optional)

User
If you want to get creative you can use this format of a style guide 
- “Using only the extracted facts, produce an event‑calendar style guide:
  - ANNUAL EVENT CALENDAR (chronological)
  - RECURRING COVERAGE OPPORTUNITIES (by theme)
  - HIGH‑PRIORITY SOURCE DIRECTORY (⭐ for 3+ mentions)
  - COUNTY QUICK FACTS (recent stories, orgs, gaps)
  - STORY TRACKER LOG (table)
  - BREAKING NEWS CONTACTS (by issue type)
  - GLOSSARY (local) and GAPS/OPPORTUNITIES
Keep bullets/tables concise. No long paragraphs.”

---

## 6) Running with Claude

Option A — Anthropic Python SDK (outline)
- Install: `pip install anthropic`
- Use batched requests for Extraction; store JSON/Markdown summaries per batch.
- Synthesize by feeding summaries to Claude with the Synthesis prompt.
- Final shaping with the Narrative Reporter’s Guide prompt.

Option B — Running with Groq 
- Install provider plugin (per your environment’s docs).
- Run stepwise, saving each pass to files, e.g.:
  - `llm -m < extract_prompt_batch_01.txt > batch_01.md`
  - `llm -m < synthesize_prompt.txt > consolidated.md`
  - `llm -m < final_narrative_prompt.txt > beat_guide.md`

Tips
- Keep prompts and inputs on disk for reproducibility.
- If you hit token limits, reduce batch size or summarize within Claude before consolidation.

---

## 7) Versioning & Validation
- Name outputs by date/model: `beat_guide_2025-12-17_sonnet.md`.
- Keep `prompts/` with the exact text used.
- Spot‑check: pick 10 events/sources at random and verify they appear in the original stories.
- Remove redundancies (e.g., sources duplicated across county + global sections).

Quality checklist
- [ ] No fabricated names/dates/claims
- [ ] County sections are narrative, not bullet lists
- [ ] Events within counties are chronological
- [ ] ⭐ markers only for people/orgs that appear 3+ times in the corpus/reference doc
- [ ] Practical reporter tips included (who to call first, what to request)

---

## 8) Troubleshooting
- Token limit errors → smaller batches; trim story bodies; first extract essentials.
- Repetition across sections → deduplicate in Synthesis step with an explicit instruction.
- Generic terminology → remind Claude: “local terms only; remove generic glossaries.”
- Over‑emphasis on state voices → add rule: “Prefer local activists/organizers/residents; include state officials only when the stories center them.”

---

## 9) Suggested File Layout
- `data/source_stories_final.json`
- `reference/important_people_organizations.md`
- `runs/2025-12-17/`
  - `extract/batch_01.md`, `batch_02.md`, …
  - `synth/consolidated.md`
  - `final/beat_guide.md` (and optional `calendar_guide.md`)
  - `prompts/*.txt`

---

## 10) Quick Start (CLI‑style)

1) Extract (repeat per batch)
- Prepare: `prompts/extract_batch_01.txt` with the Extraction prompt + stories.
- Run (example):
```bash
llm -m anthropic:sonnet < prompts/extract_batch_01.txt > runs/2025-12-17/extract/batch_01.md
```

2) Synthesize
```bash
llm -m anthropic:sonnet < prompts/synthesize.txt > runs/2025-12-17/synth/consolidated.md
```

3) Final narrative guide
```bash
llm -m anthropic:sonnet < prompts/final_narrative.txt > runs/2025-12-17/final/beat_guide.md
```

4) Optional calendar guide
```bash
llm -m anthropic:sonnet < prompts/final_calendar.txt > runs/2025-12-17/final/calendar_guide.md
```

---

## 11) Editorial Tips that Worked Best
- Lead with a mentorship tone; make the guide feel like a handoff at a coffee shop.
- Open county sections with character, not stats; weave census/context lightly.
- Always include “who to call first” and “what records to request.”
- Keep a living reference doc for ⭐ sources; update after each run as you validate.
- Use narrative in counties; reserve tables/bullets for quick‑reference appendices.

---

## 12) What to Avoid
- Quick‑stats boxes that don’t serve reporting.
- Overly generic glossaries.
- Excessive charts that repeat the same information without new value.
- Mixing state‑level voice with local pulse unless the stories do so explicitly.

---

By following this flow with Claude or Groq—batch extraction, careful synthesis, then narrative shaping—you’ll consistently generate a practical, accurate reporter’s guide that reflects the Eastern Shore’s local reality without inventing facts. Keep everything versioned, verify a sample, and iterate.
