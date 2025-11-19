#!/usr/bin/env python3
"""Filter `source_stories_final.json` to remove non-local / non-Eastern-Shore stories

Writes `source_stories_finalpt2.json` in the same folder and creates a backup of
the original source as `source_stories_final.json.bak_for_finalpt2` if not present.

Heuristics (keyword-based):
- Keep items that reference Eastern Shore local places (towns or counties)
- Exclude items that are international-conflict focused (Israel/Palestine, Gaza, Hamas, etc.)
- Exclude items that are explicitly national/statewide or other-region (Western MD, Southern MD, Delaware)
  unless they contain a local place from the Eastern Shore whitelist.
- Exclude generic opinion/columns that don't mention local places.

Adjust keyword lists inside the script if you want to relax/strengthen rules.
"""
import json
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
SRC = HERE / "source_stories_final.json"
OUT = HERE / "source_stories_finalpt2.json"
BACKUP = HERE / "source_stories_final.json.bak_for_finalpt2"


def load_src():
    with open(SRC, "r", encoding="utf-8") as f:
        return json.load(f)


def save_backup():
    if not BACKUP.exists():
        with open(SRC, "rb") as fr, open(BACKUP, "wb") as fw:
            fw.write(fr.read())
        print(f"Backup written to {BACKUP}")
    else:
        print(f"Backup already exists at {BACKUP}")


def write_out(items):
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"WROTE {OUT} with {len(items)} items")


def text_of(item):
    parts = []
    for k in ("title", "content", "author"):
        v = item.get(k)
        if v:
            parts.append(str(v))
    return "\n".join(parts).lower()


def main():
    if not SRC.exists():
        print(f"Source file not found: {SRC}")
        return

    save_backup()
    items = load_src()

    # Eastern Shore places (counties and prominent towns)
    local_places = [
        "talbot", "dorchester", "caroline", "queen anne", "queen anne's", "kent",
        "wicomico", "somerset", "worchester", "worcester", # misspelling variations
        "easton", "cambridge", "chestertown", "salisbury", "denton",
        "st. michaels", "st michaels", "oxford", "centreville", "oxford",
        "eastern shore", "delmarva"
    ]

    # International conflict keywords to exclude
    intl_keywords = [
        "israel", "palestine", "gaza", "hamas", "west bank", "jerusalem",
        "idf", "occupied", "settlement", "ukraine", "russia", "war in"
    ]

    # Other-region keywords (exclude unless local_places matched)
    other_region_keywords = [
        "western maryland", "southern maryland", "delaware", "baltimore",
        "montgomery county", "howard county", "prince george"  # broad other-region markers
    ]

    # Opinion / columns markers
    opinion_markers = ["section: columns", "section: opinion", "op-ed", "opinion", "column:"]

    kept = []
    excluded = []

    for it in items:
        txt = text_of(it)

        contains_local = any(lp in txt for lp in local_places)
        contains_intl = any(k in txt for k in intl_keywords)
        contains_other_region = any(k in txt for k in other_region_keywords) and not contains_local
        contains_opinion = any(k in txt for k in opinion_markers) and not contains_local

        # National/statewide detection: look for 'section: national' or 'section: state' or 'washington —'
        contains_national_section = ("section: national" in txt) or ("washington —" in txt) or ("section: state" in txt) and (not contains_local)

        # Statewide-only: mentions Maryland but no local place
        contains_statewide = ("maryland" in txt) and not contains_local

        reason = None
        if contains_intl:
            reason = "international_conflict"
        elif contains_other_region:
            reason = "other_region"
        elif contains_national_section:
            reason = "national_politics"
        elif contains_statewide:
            reason = "statewide_no_local"
        elif contains_opinion:
            reason = "opinion_no_local"

        if reason:
            excluded.append((it.get("title","(no title)"), reason))
        else:
            kept.append(it)

    write_out(kept)

    print(f"Original items: {len(items)}")
    print(f"Kept items: {len(kept)}")
    print(f"Excluded items: {len(excluded)}")

    # Print excluded titles grouped by reason (up to 200 lines)
    by_reason = {}
    for t, r in excluded:
        by_reason.setdefault(r, []).append(t)

    for r, ts in by_reason.items():
        print(f"\n{r}: {len(ts)} items")
        for i, t in enumerate(ts[:50], 1):
            print(f" {i}. {t}")


if __name__ == "__main__":
    main()
