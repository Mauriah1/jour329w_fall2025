#!/usr/bin/env python3
import json
from pathlib import Path

IN = Path('source_stories_no_2023_no_empty_author.json')
OUT = Path('source_stories_no_2023_no_empty_author_no_israel_poverty.json')
BAK = Path('source_stories_no_2023_no_empty_author.json.bak_for_filter2')

if not IN.exists():
    print(f"Input file not found: {IN.resolve()}")
    raise SystemExit(1)

# Backup
if not BAK.exists():
    BAK.write_bytes(IN.read_bytes())
    print(f"Backup written to {BAK}")

with IN.open('r', encoding='utf-8') as f:
    data = json.load(f)

if not isinstance(data, list):
    print('Expected top-level JSON array. Aborting.')
    raise SystemExit(1)

orig_count = len(data)

# Keywords
israel_kw = [
    'israel', 'israeli', 'palestine', 'palestinian', 'gaza', 'hamas', 'jerusalem', 'antisemit', 'jew', 'jewish'
]
poverty_kw = [
    'pover', 'poor', 'poverty', 'homeless', 'homelessness', 'food bank', 'foodbank', 'hunger', 'snack', 'welfare', 'medicaid', 'snap', 'wic', 'food pantry', 'food pantry'
]

removed_israel = 0
removed_poverty = 0
removed_both = 0
kept = []

for item in data:
    title = (item.get('title') or '')
    content = (item.get('content') or '')
    text = f"{title}\n{content}".lower()

    has_israel = any(kw in text for kw in israel_kw)
    has_poverty = any(kw in text for kw in poverty_kw)

    if has_israel and has_poverty:
        removed_both += 1
        continue
    if has_israel:
        removed_israel += 1
        continue
    if has_poverty:
        removed_poverty += 1
        continue

    kept.append(item)

OUT.write_text(json.dumps(kept, ensure_ascii=False, indent=2))

print(f"Original count: {orig_count}")
print(f"Removed (Israel/Palestine-related): {removed_israel}")
print(f"Removed (poverty-related): {removed_poverty}")
print(f"Removed (both): {removed_both}")
print(f"Final count: {len(kept)}")

# Verification - ensure no matches remain
count_israel_remaining = sum(1 for it in kept if any(kw in ( (it.get('title') or '') + '\n' + (it.get('content') or '') ).lower() for kw in israel_kw))
count_poverty_remaining = sum(1 for it in kept if any(kw in ( (it.get('title') or '') + '\n' + (it.get('content') or '') ).lower() for kw in poverty_kw))
print(f"Verification - Israel-related occurrences remaining: {count_israel_remaining}")
print(f"Verification - poverty-related occurrences remaining: {count_poverty_remaining}")

if count_israel_remaining==0 and count_poverty_remaining==0:
    print(f"WROTE {OUT.resolve()}")
else:
    print("Warning: verification found remaining matches; inspect keywords or items.")

print('Done.')
