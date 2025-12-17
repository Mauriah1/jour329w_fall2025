"""
reate a narrative beat guide for a reporter new Eastern Shore Maryland. Write it in a conversational, mentorship tone - like a veteran reporter sitting down with a newcomer to explain how this beat actually works. Use the data from from source_stories_final.json 
Two-pass approach: extract key information, then synthesize into narrative.
FOCUS: Geographic/county breakdown with community sources and glossary.
CRITICAL: Only use information from provided stories - NO fabrication.
ENHANCED: Integrates reference document of important people/organizations
"""

import json
import llm
import sys
import re
from pathlib import Path

def get_model(model_name=None):
    """Get the LLM model to use."""
    if model_name:
        return llm.get_model(model_name)
    return llm.get_model()

def clean_qwen_output(text):
    """Remove <think></think> tags from Qwen model output."""
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned.strip()

def load_reference_doc(reference_file):
    """Load the reference document with important people and organizations."""
    if not reference_file or not Path(reference_file).exists():
        return None
    
    with open(reference_file, 'r') as f:
        content = f.read()
    
    print(f"Loaded reference document: {reference_file}", file=sys.stderr)
    print("  Will prioritize people mentioned 3+ times", file=sys.stderr)
    print("  Will include 'why important' context for key sources", file=sys.stderr)
    
    return content

def extract_from_batch(stories, batch_num, model, use_qwen=False, reference_context=None):
    """First pass: extract key information with essential fields only."""
    
    essential_stories = []
    for i, story in enumerate(stories, 1):
        essential = f"Story {i}:\n"
        if isinstance(story, dict):
            if 'title' in story:
                essential += f"Title: {story['title']}\n"
            if 'headline' in story:
                essential += f"Headline: {story['headline']}\n"
            if 'content' in story:
                content = str(story['content'])[:500]
                essential += f"Content: {content}...\n"
            if 'text' in story:
                text = str(story['text'])[:500]
                essential += f"Text: {text}...\n"
            if 'date' in story:
                essential += f"Date: {story['date']}\n"
            if 'published' in story:
                essential += f"Published: {story['published']}\n"
            if 'url' in story:
                essential += f"URL: {story['url']}\n"
            if 'source' in story:
                essential += f"Source: {story['source']}\n"
        essential += "\n"
        essential_stories.append(essential)
    
    stories_text = "\n".join(essential_stories)
    
    reference_note = ""
    if reference_context:
        reference_note = f"""
**REFERENCE CONTEXT (People/Orgs mentioned 3+ times):**
When you encounter these people/organizations in the stories, note them as HIGH PRIORITY:
{reference_context[:2000]}
"""
    
    prompt = f"""Analyze these {len(stories)} Maryland Eastern Shore stories about Race & Diversity. Extract key information:

**CRITICAL RULE: ONLY extract information that is EXPLICITLY stated in these stories. DO NOT make up, infer, or fabricate any names, dates, events, or details. If something is not in the stories, DO NOT include it.**

{reference_note}

**COUNTIES & DEMOGRAPHICS:** Which counties mentioned, racial/ethnic composition, demographic changes
**KEY THEMES BY COUNTY:** (2-3 sentences per county)
**COMMUNITY SOURCES:** Name (Role/Organization) - Focus on LOCAL leaders, activists, residents - NOT state officials (1 line each, max 8)
  - **Mark with [HIGH PRIORITY] if person appears in reference context above**
  - **Count how many times each person is mentioned across stories**
**ORGANIZATIONS:** Name - what they do (1 line each, max 5)
  - **Mark with [HIGH PRIORITY] if organization appears in reference context above**
  - **Count how many times each org is mentioned across stories**
**MAJOR EVENTS BY LOCATION:** County/Town: Date: Event description - COUNT how many events per county (1 line each, max 8)
**SPECIFIC TERMS/PHRASES:** ONLY Shore-specific local terminology, NOT general terms like "ICE arrest"
**KEYWORDS & FRAMING:** How is race discussed? What words/phrases appear repeatedly?
**STORY REFERENCES:** Note story titles or URLs for major events
**COVERAGE PATTERNS:** Story types, voices heard, local vs. state sources (2-3 sentences)

Focus on: LOCAL geographic patterns, racial demographics, COMMUNITY voices (activists, faith leaders, residents) NOT state politicians.

ONLY USE INFORMATION FROM THE STORIES BELOW. DO NOT FABRICATE.

STORIES:
{stories_text}

CONCISE SUMMARY:"""
    
    print(f"Processing batch {batch_num}...", file=sys.stderr)
    
    try:
        response = model.prompt(prompt)
        result = response.text()
    except Exception as e:
        if "413" in str(e) or "rate_limit" in str(e) or "too large" in str(e).lower():
            print(f"⚠️  Token limit exceeded in batch {batch_num}, falling back to gpt-oss-20b...", file=sys.stderr)
            fallback_model = get_model("groq/openai/gpt-oss-20b")
            response = fallback_model.prompt(prompt)
            result = response.text()
        else:
            raise
    
    if use_qwen:
        result = clean_qwen_output(result)
    
    return result

def synthesize_intermediate(summaries, level, model, use_qwen=False):
    """Synthesize summaries - concise version with automatic fallback."""
    combined = "\n\n---\n\n".join(
        f"SECTION {i+1}:\n{summary}" 
        for i, summary in enumerate(summaries)
    )
    
    prompt = f"""Consolidate these {len(summaries)} summaries. Keep it CONCISE.

**CRITICAL: Only use information from these summaries. DO NOT add new names, events, or details that aren't in the summaries.**

Combine and deduplicate by COUNTY:
- Counties (names, racial demographics, key issues) - COUNT events per county
- Community sources (name, role, county) - Focus on LOCAL leaders NOT state politicians
  - **Preserve [HIGH PRIORITY] markers for people mentioned 3+ times**
  - **Keep mention counts for key sources**
- Organizations (name, county, significance)
  - **Preserve [HIGH PRIORITY] markers for orgs mentioned 3+ times**
  - **Keep mention counts**
- Themes by county (major issues)
- Events (county, date, what happened) - Keep chronological order
- Local Shore-specific terms ONLY
- Keywords and framing patterns
- Story references (titles, URLs if available)

Remove duplicates. Keep important items. Be brief. Maintain chronological order for events.

DO NOT MAKE UP ANY INFORMATION. ONLY USE WHAT'S IN THE SUMMARIES.

SUMMARIES:
{combined}

CONSOLIDATED:"""
    
    print(f"Consolidating level {level} ({len(summaries)} summaries)...", file=sys.stderr)
    
    try:
        response = model.prompt(prompt)
        result = response.text()
    except Exception as e:
        if "413" in str(e) or "rate_limit" in str(e) or "too large" in str(e).lower():
            print(f"⚠️  Token limit exceeded at level {level}, falling back to gpt-oss-20b...", file=sys.stderr)
            fallback_model = get_model("groq/openai/gpt-oss-20b")
            response = fallback_model.prompt(prompt)
            result = response.text()
        else:
            raise
    
    if use_qwen:
        result = clean_qwen_output(result)
    
    return result

def synthesize_guide(batch_summaries, topic, model, max_summaries_per_level=3, use_qwen=False, reference_content=None):
    """Synthesize batch summaries into county-focused beat book with glossary."""
    
    if len(batch_summaries) <= max_summaries_per_level:
        combined = "\n\n---\n\n".join(
            f"BATCH {i+1}:\n{summary}" 
            for i, summary in enumerate(batch_summaries)
        )
    else:
        current_level = batch_summaries
        level = 1
        
        while len(current_level) > max_summaries_per_level:
            next_level = []
            for i in range(0, len(current_level), max_summaries_per_level):
                group = current_level[i:i+max_summaries_per_level]
                consolidated = synthesize_intermediate(group, level, model, use_qwen)
                next_level.append(consolidated)
            current_level = next_level
            level += 1
        
        combined = "\n\n---\n\n".join(
            f"SECTION {i+1}:\n{summary}" 
            for i, summary in enumerate(current_level)
        )
    
    reference_instruction = ""
    if reference_content:
        reference_instruction = f"""

**REFERENCE DOCUMENT - IMPORTANT PEOPLE & ORGANIZATIONS:**
The following people and organizations were mentioned 3+ times across all stories and are HIGH PRIORITY sources:

{reference_content[:3000]}

**When writing the Community Sources Directory and Key Players sections:**
- Prioritize these HIGH PRIORITY sources (mentioned 3+ times)
- Include the "why important" context from the reference document
- Add contact information if available in the reference
- Mark HIGH PRIORITY sources with ⭐ symbol
"""
    
    prompt = f"""Create a narrative beat guide for a reporter new to both Maryland's Eastern Shore AND covering race and diversity. Write it in a conversational, mentorship tone - like a veteran Shore reporter sitting down with a newcomer to explain how this beat actually works. Use ONLY the data from the summaries below.
{reference_instruction}
**CRITICAL**: Prioritize LOCAL knowledge and sources over generic beat reporting advice. This guide should be deeply rooted in the Shore's eight counties: Talbot, Dorchester, Kent, Queen Anne's, Caroline, Wicomico, Somerset, Worcester.

**1. Understanding the Race Beat on the Eastern Shore**
Open with a narrative overview that sets the scene (2-3 paragraphs):
- What does covering race and diversity on the Shore actually mean day-to-day? This isn't Baltimore or DC - it's eight distinct counties with different rhythms, demographics, and tensions
- Describe the rhythm of this beat: what a typical week looks like, what demands constant attention vs. what needs deeper investigation
- Explain the major story threads from 2024-2025 that run through everything and how they connect geographically
- What makes the Shore different? Paint the picture: "When you're working this beat, you'll find yourself..."

**2. The Players You'll Get to Know**
Don't just list names - tell stories about who these LOCAL people are, why reporters keep going back to them, what they're good for (3-4 paragraphs):
- Describe the power dynamics: who influences what, which institutions matter most and why
- Focus on COMMUNITY voices: activists, organizers, faith leaders, long-time residents (mark sources with ⭐ if mentioned 3+ times)
- Organizations that shape coverage across the Shore
- Include practical tips woven into the narrative: "When X happens in Wicomico, call Y first because..." or "Z in Talbot always has good context on..."
- Explain WHY these sources matter, not just who they are. What stories are they connected to? What do they bring to coverage?

Use natural prose, not lists. Make this read like advice from a mentor: "You'll find that..." "Keep in mind..."

**3. How Stories Get Written Here**
Analyze the actual writing patterns and coverage from the summaries (3-4 paragraphs):
- What makes a strong Shore race and diversity story? Show patterns in the actual coverage
- Describe sourcing strategies: who gets quoted, in what order, why
- Point out what works with specific examples from story titles, URLs, key quotes
- Explain how Shore coverage differs from urban reporting
- What keywords and frames appear most often? How are stories structured?

No tables - integrate examples naturally into the narrative.

**4. Building Your Beat**
Walk through HOW to develop this beat from day one (3-4 paragraphs of practical advice):
- How to develop sources (not just who they are, but HOW to build those relationships)
- What records to request, when, and why
- How to balance reactive coverage with deeper investigation
- Give concrete advice woven into narrative: "Every Monday, you'll want to check..." or "When you hear about X, that's your cue to..."
- How to navigate the eight-county geography
- What institutional knowledge you need to build

**5. County-by-County Breakdown**
For EACH of the eight Shore counties that appear in the summaries, write one rich narrative section (3-4 paragraphs each):
- What makes this county tick: demographics, main issues, unique character
- The towns and communities you'll be covering
- Key events from 2024-25 in CHRONOLOGICAL ORDER - don't just list them, explain what they reveal about the county
- The LOCAL people (⭐ mark those mentioned 3+ times) who matter here and WHY
- Practical reporting tips specific to this county
- Census data woven in naturally: race/ethnicity, poverty rates, healthcare access, education levels (or note "Census data not in summaries")

Write each county as flowing narrative paragraphs that tell the county's story. Use direct address: "In Caroline County, you'll find..." If stories mention people/events OUTSIDE the Shore, note briefly as "[NAME] (Outside Shore)" but keep focus local.

**6. Stories Waiting to Be Told**
Present 3-5 story ideas as narrative pitches, not bullet points (full paragraphs for each):
- Here's the angle, here's why it matters to Shore communities
- Here's who to talk to first (use LOCAL sources from earlier sections)
- Here's the document that will unlock it
- Explain the reporting process: "Start by..., then..., watch out for..."
- Make these DIFFERENT from what's already been covered
- Include county-specific stories and comparative angles across counties

**7. Themes Across Counties**
Identify and explain major themes from the summaries (3-4 narrative paragraphs):
- What issues appear across multiple counties? How do they connect?
- Where do you see spikes in certain types of coverage?
- Give specific examples from specific places with story references
- Explain what these patterns tell you about the Shore
- How do themes in one county echo or differ in another?

**8. Coverage Analysis**
Analyze patterns and gaps (3-4 paragraphs):
- Which counties get more coverage and why? What's being missed?
- What types of sources appear most? What voices dominate? What communities aren't being heard?
- Break down source diversity across counties - synthesize patterns, don't repeat
- What story angles are missing? What needs follow-up?
- Where are the geographic and demographic gaps?

**9. A Day-to-Day: What It May Look Like for You**
Close with practical guidance on the daily rhythm (2-3 paragraphs):
- Walk through what a typical week actually looks like on this beat
- Morning routines: what to check, who to call
- How to divide time between counties
- Balancing daily coverage with enterprise work
- Building and maintaining source relationships across eight counties
- What to do when big news breaks vs. quiet news days

**10. Navigating Sensitivities & Interview Tips**
Write this as narrative prose (2-3 paragraphs) covering key sensitivities by location:
- **Talbot**: ICE activism and the Frederick Douglass narrative may evoke trauma; explain how to ask about personal experiences with law enforcement and heritage with care
- **Calvert/Sussex**: Hate-crime charges involve minors; explain how to approach with caution, emphasize confidentiality
- **Cambridge**: Native-American communities value respectful language; explain how to avoid colonial terminology
- **Caroline**: LGBTQ and Juneteenth events intersect; explain how to ask about these communities navigating shared spaces
- **Turner Station**: Vandalism impacts community pride; explain how to ask about healing initiatives

**SECTION 11: Navigating Sensitivities & Interview Tipsas 2-3 narrative paragraphs covering:

Talbot: ICE activism & Frederick Douglass trauma
Calvert/Sussex: Hate crimes involving minors
Cambridge: Native American respectful language
Caroline: LGBTQ & Juneteenth intersections
Turner Station: Vandalism & healing initiatives
Write this conversationally: "When you're covering X in [County], remember that..." Emphasize leading with respect, giving people control over their stories, recognizing interviews as acts of trust.

**ESSENTIAL RULES:**
- Use ONLY real names, dates, and events from the summaries - NO fabrication
- Write in full prose - NO bullet points, NO lists, NO tables anywhere
- Always prioritize LOCAL leaders over state politicians
- Write ONE rich narrative per county (3-4 flowing paragraphs)
- Include 2+ specific events per county
- Keep everything chronological where relevant
- Label non-Shore people/orgs as "[NAME] (Outside Shore)"
- Never use "public servant" - use "resident," "community member," or specific titles
- Mark sources with 3+ mentions as ⭐
- Always explain WHY sources matter, not just who they are
- Conversational mentorship tone throughout - direct address, "you'll find that..."
- Short paragraphs, specific examples, voice-driven
- Make this something a reporter would actually want to read and refer back to

Write this as a 1-2 page guide per section that reads like a conversation, not a data dump.

SUMMARIES:
{combined}

CREATE THE GUIDE:"""
    
    print("Synthesizing county-focused guide with HIGH PRIORITY sources...", file=sys.stderr)
    
    try:
        response = model.prompt(prompt)
        result = response.text()
    except Exception as e:
        if "413" in str(e) or "rate_limit" in str(e) or "too large" in str(e).lower():
            print(f"⚠️  Token limit exceeded in final generation, falling back to gpt-oss-20b...", file=sys.stderr)
            fallback_model = get_model("groq/openai/gpt-oss-20b")
            response = fallback_model.prompt(prompt)
            result = response.text()
        else:
            raise
    
    if use_qwen:
        result = clean_qwen_output(result)
    
    return result

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate a county-focused Beat Book for Maryland Eastern Shore (ONLY from source stories - NO fabrication)'
    )
    parser.add_argument('input_file', nargs='?', default='source_stories_final.json',
                       help='Path to JSON file (default: source_stories_final.json)')
    parser.add_argument('-o', '--output', default='reporter_guide_county.txt',
                       help='Output file (default: reporter_guide_county.txt)')
    parser.add_argument('-r', '--reference', default=None,
                       help='Path to reference markdown with important people/orgs (optional)')
    parser.add_argument('-b', '--batch-size', type=int, default=15,
                       help='Stories per batch (default: 15)')
    parser.add_argument('-m', '--model', 
                       default='groq/meta-llama/llama-3.3-70b-versatile',
                       choices=[
                           'groq/openai/gpt-oss-20b',
                           'groq/openai/gpt-oss-120b',
                           'groq/meta-llama/llama-3.3-70b-versatile',
                           'groq/meta-llama/llama-4-maverick-17b-128e-instruct',
                           'groq/moonshotai/kimi-k2-instruct-0905',
                           'groq/qwen/qwen3-32b'
                       ],
                       help='LLM model to use (default: llama-3.3-70b-versatile)')
    parser.add_argument('-t', '--topic', default='Race & Diversity',
                       help='Topic name (default: Race & Diversity)')
    parser.add_argument('--summaries-only', action='store_true',
                       help='Save batch summaries without synthesis')
    parser.add_argument('--debug', action='store_true',
                       help='Save intermediate outputs')
    parser.add_argument('--max-consolidate', type=int, default=3,
                       help='Max summaries to consolidate at once (default: 3)')
    
    args = parser.parse_args()
    
    use_qwen = args.model == 'groq/qwen/qwen3-32b' if args.model else False
    
    # Load reference document if provided
    reference_content = None
    if args.reference:
        reference_content = load_reference_doc(args.reference)
    
    print(f"Loading stories from {args.input_file}...", file=sys.stderr)
    print(f"CRITICAL: Will ONLY use information from stories in {args.input_file}", file=sys.stderr)
    print(f"NO FABRICATION of names, events, or data will be allowed", file=sys.stderr)
    
    try:
        with open(args.input_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    if isinstance(data, list):
        stories = data
    elif isinstance(data, dict) and 'stories' in data:
        stories = data['stories']
    elif isinstance(data, dict) and 'articles' in data:
        stories = data['articles']
    else:
        print("Error: JSON structure not recognized.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Loaded {len(stories)} stories", file=sys.stderr)
    
    model = get_model(args.model)
    print(f"Using model: {model.model_id}", file=sys.stderr)
    print(f"FOCUS: County-by-county breakdown with LOCAL community sources", file=sys.stderr)
    print(f"INCLUDES: Keyword/framing analysis and census data section", file=sys.stderr)
    print(f"PRIORITY: People/orgs mentioned 3+ times (marked with ⭐)", file=sys.stderr)
    print(f"SOURCE: ONLY {args.input_file} - NO external information", file=sys.stderr)
    if use_qwen:
        print("NOTE: Qwen model - will strip <think> tags", file=sys.stderr)
    
    batch_summaries = []
    num_batches = (len(stories) + args.batch_size - 1) // args.batch_size
    
    print(f"Processing {num_batches} batches (size: {args.batch_size})", file=sys.stderr)
    
    # Pass reference context to extraction phase
    reference_context = reference_content[:2000] if reference_content else None
    
    for i in range(0, len(stories), args.batch_size):
        batch = stories[i:i+args.batch_size]
        batch_num = i // args.batch_size + 1
        summary = extract_from_batch(batch, batch_num, model, use_qwen, reference_context)
        batch_summaries.append(summary)
        
        if args.debug:
            debug_file = f"debug_batch_{batch_num:03d}.md"
            with open(debug_file, 'w') as f:
                f.write(summary)
            print(f"  Saved: {debug_file}", file=sys.stderr)
    
    if args.debug:
        total_chars = sum(len(s) for s in batch_summaries)
        total_words = sum(len(s.split()) for s in batch_summaries)
        print(f"\nDEBUG: Total summaries:", file=sys.stderr)
        print(f"  {total_chars:,} characters", file=sys.stderr)
        print(f"  {total_words:,} words", file=sys.stderr)
        print(f"  ~{total_words * 1.3:.0f} tokens (estimate)", file=sys.stderr)
    
    if args.summaries_only:
        output_file = args.output.replace('.md', '_summaries.md')
        with open(output_file, 'w') as f:
            for i, summary in enumerate(batch_summaries, 1):
                f.write(f"\n\n## Batch {i}\n\n{summary}\n")
        print(f"Batch summaries saved to {output_file}", file=sys.stderr)
        return
    
    guide = synthesize_guide(batch_summaries, args.topic, model, 
                           max_summaries_per_level=args.max_consolidate, 
                           use_qwen=use_qwen,
                           reference_content=reference_content)
    
    with open(args.output, 'w') as f:
        f.write(f"# Reporter's Beat Book: {args.topic}\n")
        f.write(f"## Maryland's Eastern Shore - County-by-County Guide (2024-2025)\n\n")
        f.write(f"**SOURCE: Information extracted ONLY from stories in {args.input_file}**\n")
        f.write(f"**NO fabricated names, events, or data included**\n")
        if reference_content:
            f.write(f"**HIGH PRIORITY SOURCES: People/organizations mentioned 3+ times marked with ⭐**\n")
        f.write("\n---\n\n")
        f.write(guide)
    
    print(f"\nCounty-Focused Beat Book saved to {args.output}", file=sys.stderr)
    print(f"  Processed {len(stories)} stories in {num_batches} batches", file=sys.stderr)
    print(f"  PRIMARY FOCUS: Eastern Shore counties with LOCAL community leaders", file=sys.stderr)
    print(f"  HIGH PRIORITY: Sources mentioned 3+ times marked with ⭐", file=sys.stderr)
    print(f"  INCLUDES: Census data, keyword analysis, chronological story arcs", file=sys.stderr)
    print(f"  DATA SOURCE: ONLY {args.input_file} - no fabrication", file=sys.stderr)

if __name__ == '__main__':
    main()