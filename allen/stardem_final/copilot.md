# Copilot Conversation Summary: StarDem Final

**Date:** December 17, 2025

## Context
- Folder: `allen/stardem_final`
- Latest command (terminal): `python generate_reporter_guide_revised.py source_stories_final.json -m groq/openai/gpt-oss-120b -r important_people_organizations.md -o beat_guide.md`
- Inputs: `source_stories_final.json` (story corpus), `important_people_organizations.md` (reference, 3+ mentions prioritized)
- Output: `beat_guide.md` (narrative reporter’s guide); `beat_guide.txt` also present
- `notes.md` is currently empty.

## Approach
- Two-pass pipeline in `generate_reporter_guide_revised.py`:
  - **Extract**: Batch stories → essential fields (title, headline, content/text snippet, date/published, url, source) with strict "no fabrication" rule; reference context injected and HIGH PRIORITY markers preserved; optional Qwen cleanup.
  - **Synthesize**: Hierarchical consolidation to keep county focus, mention counts, HIGH PRIORITY flags, events chronologically ordered; fails over to smaller model on token/rate issues.
  - **Guide assembly**: Final prompt builds county-focused narrative guide with glossary, community sources, coverage patterns; uses specified model (here `groq/openai/gpt-oss-120b`).
- Prompt design (`prompt.txt`): mentorship tone, 10-section structure, heavy county grounding (Talbot, Dorchester, Kent, Queen Anne's, Caroline, Wicomico, Somerset, Worcester), story-anchored, no fabrication, local over generic advice.

## Generated Guide Highlights (`beat_guide.md`)
- Mentorship narrative framing a newcomer reporter’s onboarding.
- Sections cover: understanding the race/diversity beat; key players with ⭐ for 3+ mentions; writing patterns and sourcing sequences; beat-building playbook; detailed county-by-county narratives; story ideas; cross-county themes; yearly arcs; glossary/framing; coverage gaps/opportunities.
- High-priority sources surfaced: Carl Snowden, Victoria Gómez Lozano, Tina Jones, Kyle O’Donnell, Jaelon Moaney, Dave Stepp, Keasha Haythe, Lajan Cephas; emphasis on local activists and organizers.
- County narratives (example from Talbot/Dorchester): blend events (Juneteenth, Pride, DEI votes, bridge renaming), power dynamics, reporting tips, and who to call first.

## Observations
- The run completed successfully with the gpt-oss-120b model and reference doc, producing a prose-heavy, locally grounded guide.
- Notes/documentation still needed: `notes.md` is empty; consider recording runs, models, prompts, and evaluation.

## Suggested Next Steps
- Document the run in `notes.md` (command, model, reference file, outputs, impressions).
- Spot-check `beat_guide.md` for hallucinations or mis-placements against source stories.
- If size is large, consider a lighter concise version for quick reference while keeping this narrative edition as the full guide.
