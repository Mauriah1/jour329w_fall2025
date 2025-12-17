#!/usr/bin/env python3
import json
from pathlib import Path

IN = Path('source_stories_final.json')
OUT = Path('source_stories_no_2023_no_empty_author.json')
BAK = Path('source_stories_final.json.bak_for_filter')

if not IN.exists():
    print(f"Input file not found: {IN.resolve()}")
    raise SystemExit(1)

# Make a backup if not already present
if not BAK.exists():
    BAK.write_bytes(IN.read_bytes())
    print(f"Backup written to {BAK}")

with IN.open('r', encoding='utf-8') as f:
    data = json.load(f)

if not isinstance(data, list):
    print('Expected top-level JSON array. Aborting.')
    raise SystemExit(1)

orig_count = len(data)

kept = []
removed_2023 = 0
removed_empty_author = 0
removed_both = 0
for item in data:
    # date may be like '2023-08-04' or 'August 4, 2023' etc. We'll try to detect year '2023' anywhere
    date = item.get('date','')
    author = item.get('author', None)
    has_2023 = False
    if isinstance(date, str) and '2023' in date:
        has_2023 = True
    # treat empty author as empty string or whitespace-only or missing
    empty_author = (author is None) or (isinstance(author, str) and author.strip() == '')

    if has_2023 and empty_author:
        removed_both += 1
        continue
    if has_2023:
        removed_2023 += 1
        continue
    if empty_author:
        removed_empty_author += 1
        continue
    kept.append(item)

OUT.write_text(json.dumps(kept, ensure_ascii=False, indent=2))

print(f"Original count: {orig_count}")
print(f"Removed (2023 only): {removed_2023}")
print(f"Removed (empty author only): {removed_empty_author}")
print(f"Removed (both 2023 and empty author): {removed_both}")
print(f"Final count: {len(kept)}")

# quick validation checks
# 1) ensure no 2023 in any kept item's date
count_2023_remaining = sum(1 for it in kept if isinstance(it.get('date',''), str) and '2023' in it.get('date',''))
count_empty_author_remaining = sum(1 for it in kept if (it.get('author') is None) or (isinstance(it.get('author'), str) and it.get('author','').strip()=='') )
print(f"Verification - 2023 occurrences remaining: {count_2023_remaining}")
print(f"Verification - empty-author occurrences remaining: {count_empty_author_remaining}")

if count_2023_remaining==0 and count_empty_author_remaining==0:
    print(f"WROTE {OUT.resolve()}")
else:
    print("Warning: verification failed - some items remain that match removal criteria.")

print('Done.')
