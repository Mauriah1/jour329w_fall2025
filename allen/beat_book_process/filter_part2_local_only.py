#!/usr/bin/env python3
import json
from pathlib import Path

IN = Path('source_stories_30_2024_30_2025.json')
OUT = Path('source_stories_30_2024_30_2025_part2.json')
BAK = Path(str(OUT) + '.bak')

if not IN.exists():
    print(f'Input file not found: {IN.resolve()}')
    raise SystemExit(1)

data = json.loads(IN.read_text(encoding='utf-8'))
if not isinstance(data, list):
    print('Expected top-level array in input')
    raise SystemExit(1)

# Keywords / heuristics
local_places = [
    'talbot', 'dorchester', 'caroline', "queen anne", 'kent', 'wicomico', 'worcester', 'somerset',
    'eastern shore', 'easton', 'cambridge', 'federalsburg', 'chestertown', 'oxford', 'st. michaels',
    'talbot county', 'dorchester county', 'caroline county', 'queen anne', 'queen anne\'s', 'kent county',
    'salisbury', 'kent island'
]

national_politics_kw = [
    'president','white house','congress','senate','house of representatives','house speaker','election','campaign','voting rights act','supreme court','donald trump','joe biden','speaker'
]
other_regions_kw = ['western maryland','southern maryland','delaware','baltimore city','anne arundel','montgomery county','prince george','howard county']
intl_kw = ['israel','palestine','gaza','hamas','ukraine','russia','foreign']
statewide_kw = ['statewide','governor','maryland general assembly','general assembly','state leaders','statewide']
opinion_sections = ['opinion','columns','editorial','letter to the editor']

excluded = []
kept = []

for item in data:
    title = (item.get('title') or '')
    content = (item.get('content') or '')
    section = (item.get('section') or '')
    authors = (item.get('author') or '')
    text = f"{title}\n{content}\n{section}\n{authors}".lower()

    # helpers
    has_local = any(lp in text for lp in local_places)
    has_national = any(kw in text for kw in national_politics_kw)
    has_other_region = any(kw in text for kw in other_regions_kw)
    has_international = any(kw in text for kw in intl_kw)
    has_statewide = any(kw in text for kw in statewide_kw)
    is_opinion = any(sec in text for sec in opinion_sections)

    reason = None

    # Exclude international conflicts always
    if has_international:
        reason = 'international_conflict'
    # Exclude other regions unless also local
    elif has_other_region and not has_local:
        reason = 'other_region'
    # Exclude national politics unless local impact
    elif has_national and not has_local:
        reason = 'national_politics'
    # Exclude statewide-only issues without Eastern Shore angle
    elif has_statewide and not has_local:
        reason = 'statewide_no_local'
    # Exclude generic opinion/columns without local relevance
    elif is_opinion and not has_local:
        reason = 'opinion_no_local'

    if reason:
        excluded.append({'title': title, 'reason': reason})
    else:
        kept.append(item)

# Backup output if exists
if OUT.exists() and not BAK.exists():
    BAK.write_bytes(OUT.read_bytes())

OUT.write_text(json.dumps(kept, ensure_ascii=False, indent=2), encoding='utf-8')

print(f'Original items: {len(data)}')
print(f'Kept items: {len(kept)}')
print(f'Excluded items: {len(excluded)}')

# breakdown
from collections import Counter
reasons = Counter(e['reason'] for e in excluded)
for r,c in reasons.items():
    print(f'  {r}: {c}')

print('\nExcluded titles:')
for i,e in enumerate(excluded, start=1):
    print(f"{i}. ({e['reason']}) {e['title']}")

print('\nWROTE', OUT.resolve())
print('Done.')
