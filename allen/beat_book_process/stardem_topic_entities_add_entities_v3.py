#!/usr/bin/env python3
"""
ENHANCED VERSION: Extreme focus on extracting AUTHORS and PEOPLE
This version prioritizes finding authors and extracting all people mentioned.

Extract standard entities from Star-Democrat race and diversity stories.
Input: topic_stories.json (stories already about race/diversity)
Output: stories_with_entities_v3.json
"""

import json
import subprocess
import sys
import argparse
from datetime import datetime

# Maryland county and municipality data
maryland_county_list = [
    {"county": "Dorchester County", "municipalities": "Brookview, Cambridge, Church Creek, Crapo, Crocheron, East New Market, Eldorado, Fishing Creek, Galestown, Hurlock, Linkwood, Madison, Rhodesdale, Secretary, Taylors Island, Toddville, Vienna, Wingate, Woolford"},
    {"county": "Caroline County", "municipalities": "Denton, Federalsburg, Goldsboro, Greensboro, Henderson, Hillsboro, Marydel, Preston, Ridgely, Templeville, Choptank, West Denton, Williston, American Corner, Andersontown, Baltimore Corner, Bethlehem, Brick Wall Landing, Burrsville, Gilpin Point, Harmony, Hickman, Hobbs, Jumptown, Linchester, Oakland, Oil City, Tanyard, Two Johns, Reliance, Whiteleysburg"},
    {"county": "Kent County", "municipalities": "Betterton, Chestertown, Galena, Millington, Rock Hall, Butlertown, Chesapeake Landing, Edesville, Fairlee, Georgetown, Kennedyville, Still Pond, Tolchester, Worton, Chesterville, Golts, Hassengers Corner, Langford, Lynch, Massey, Pomona, Sassafras, Sharpstown, Tolchester Beach"},
    {"county": "Queen Anne's County", "municipalities": "Barclay, Centreville, Church Hill, Millington, Queen Anne, Queenstown, Sudlersville, Templeville, Chester, Grasonville, Kent Narrows, Kingstown, Romancoke, Stevensville, Crumpton, Dominion, Ingleside, Love Point, Matapeake, Price, Ruthsburg"},
    {"county": "Talbot County", "municipalities": "Easton, Oxford, Queen Anne, Saint Michaels, Trappe, Cordova, Tilghman Island, Anchorage, Bellevue, Bozman, Claiborne, Copperville, Doncaster, Fairbanks, Lewistown, Lloyd Landing, Matthews, McDaniel, Neavitt, Newcomb, Royal Oak, Sherwood, Tunis Mills, Unionville, Wittman, Windy Hill, Woodland, Wye Mills, Dover, York, Wyetown"},
    {"county": "Prince George's County", "municipalities": "Bowie, College Park, District Heights, Glenarden, Greenbelt, Hyattsville, Laurel, Mount Rainier, New Carrollton, Seat Pleasant, Berwyn Heights, Bladensburg, Brentwood, Capitol Heights, Cheverly, Colmar Manor, Cottage City, Eagle Harbor, Edmonston, Fairmount Heights, Forest Heights, Landover Hills, Morningside, North Brentwood, Riverdale Park, University Park, Upper Marlboro"},
    {"county": "Calvert County", "municipalities": "Adelina, Barstow, Bowens, Chaneyville, Dares Beach, Dowell, Johnstown, Lower Marlboro, Mutual, Parran, Pleasant Valley, Port Republic, Scientists Cliffs, Stoakley, Sunderland, Wallville, Wilson, Chesapeake Beach, North Beach, Broomes Island, Calvert Beach, Chesapeake Ranch Estates, Drum Point, Dunkirk, Huntingtown, Long Beach, Lusby, Owings, Prince Frederick, St. Leonard, Solomons"},
    {"county": "Talbot County", "municipalities": "Easton, Oxford, Queen Anne, Saint Michaels, Trappe, Cordova, Tilghman Island"},
    {"county": "Baltimore City", "municipalities": "Baltimore City"}
]

def create_extraction_prompt(story):
    """Create prompt with EXTREME emphasis on finding authors and people."""
    
    title = story.get('headline', story.get('title', ''))
    text = story.get('text', '')
    date = story.get('date', '')
    docref = story.get('docref', '')
    
    county_info = "\n".join([f"- {item['county']}: {item['municipalities']}" for item in maryland_county_list])
    
    prompt = f"""⚠️ CRITICAL PRIORITY: AUTHOR and PEOPLE must be extracted if they exist AT ALL.

ARTICLE LINK: {docref}
TITLE: {title}
DATE: {date}

FULL TEXT:
{text}

==========================================================================
TASK 1 - AUTHOR (CHECK EVERYWHERE - DO NOT MISS THIS)
==========================================================================

Search for author in this order:

BEGINNING (first 3 lines):
- "By [Name]"
- "By: [Name]"
- "[Name], Staff Writer"  
- "[Name] | Staff Writer"
- "Written by [Name]"

END (last 3 lines):
- "[Name] can be reached at..."
- "Contact [Name] at..."

ANYWHERE:
- Look for ANY line with a name + job title
- Look for email with name

EXAMPLES:
"By Jane Smith" → Extract: Jane Smith
"John Doe, Staff Writer" → Extract: John Doe  
"Contact Mary at..." → Extract: Mary

⚠️ Only use "N/A" if you checked EVERYWHERE and found NOTHING.

==========================================================================
TASK 2 - PEOPLE (EXTRACT EVERYONE MENTIONED BY NAME)
==========================================================================

Read EVERY sentence. Extract EVERY person's name you see.

WHO TO INCLUDE:

1. ANYONE IN QUOTES (CRITICAL):
   - If someone "said" something, they MUST be in the list
   - Look for quotation marks ""
   - Example: 'Smith said "..."' → MUST include Smith

2. ANYONE WITH A TITLE:
   - Mayor, Governor, Senator, Councilman, Chief, Director, Rev., Dr., etc.
   - Example: "Mayor John Smith" → Include with title

3. ANYONE DOING SOMETHING:
   - "[Name] voted", "[Name] organized", "[Name] attended"

4. ANY NAMED PERSON:
   - Residents, parents, students, victims, anyone with a name
   - Example: "Parent Maria Garcia" → Include her

FORMAT: "Title Name; Title Name; Title Name"
Example: "Mayor John Smith; Rev. Maria Garcia; Dr. James Lee; Sarah Martinez"

⚠️ CRITICAL: "John Smith", "Maria Garcia", "James Lee" are FORMAT EXAMPLES ONLY.
DO NOT use these placeholder names in your response.
Extract the ACTUAL REAL names from the article text above.
Use names that actually appear in the article, not the example names shown here.

⚠️ Only use "N/A" if NO names appear ANYWHERE.

==========================================================================
TASK 3 - ORGANIZATIONS (LIST ACTUAL NAMES, NOT "ORG 1, ORG 2")
==========================================================================

Extract ALL organizations mentioned. Use FULL, SPECIFIC NAMES.

LOOK FOR THESE TYPES:

**GOVERNMENT ENTITIES:**
- City/County Councils: "Easton Town Council", "Talbot County Council"
- Boards: "Talbot County Board of Education", "Cambridge Board of Commissioners"
- Departments: "Easton Police Department", "Maryland Department of Natural Resources"
- Agencies: "Maryland State Police", "Dorchester County Sheriff's Office"

**SCHOOLS & EDUCATION:**
- Schools: "Easton High School", "Cambridge-South Dorchester High School"
- Systems: "Talbot County Public Schools", "Caroline County Public Schools"
- Universities: "University of Maryland Eastern Shore", "Chesapeake College"

**NONPROFITS & COMMUNITY:**
- Civil Rights: "NAACP Talbot County Branch", "NAACP Cambridge-Dorchester Branch"
- Community: "Talbot County Community Foundation", "Dorchester Community Center"
- Advocacy: "Talbot County Committee for Racial Justice", "Eastern Shore Coalition"

**CHURCHES & RELIGIOUS:**
- Full names: "Bethel AME Church", "First Baptist Church", "St. Paul's Methodist Church"
- Not just "the church" - use the actual name

**BUSINESSES:**
- Hospitals: "University of Maryland Shore Regional Health", "Talbot Medical Center"
- Companies: "Chesapeake Bay Maritime Museum", "Talbot County Chamber of Commerce"
- Named businesses: Use actual business names, not "local business"

**CIVIC GROUPS:**
- "Easton Rotary Club", "Cambridge Lions Club", "Talbot Historical Society"

FORMAT EXAMPLES (Use ACTUAL names like these):
- Good: "Talbot County Council; Easton High School; NAACP; Bethel AME Church"
- Bad: "Org 1; Org 2; Org 3"
- Bad: "the council; a local school; a church"

⚠️ CRITICAL: "Talbot County Council", "Easton High School", "NAACP", "Bethel AME Church" are FORMAT EXAMPLES showing the STYLE of names to use.
DO NOT copy these exact organization names into your response.
Extract the ACTUAL organizations that appear in the article text above.
Use real organization names from the article, not the example names shown here.

⚠️ Use FULL, SPECIFIC organization names. Only use "N/A" if NO organizations mentioned.

==========================================================================
TASK 4 - MARYLAND COUNTIES (LIST ACTUAL COUNTY NAMES)
==========================================================================

MARYLAND COUNTY REFERENCE:
{county_info}

TASK: Identify which specific Maryland COUNTY or COUNTIES this story is about.

HOW TO FIND COUNTIES:

1. **DIRECT MENTIONS** - Look for these exact names:
   - "Talbot County", "Dorchester County", "Caroline County", "Kent County"
   - "Queen Anne's County", "Wicomico County", "Worcester County"
   - "Somerset County", "Prince George's County", "Baltimore City"

2. **MUNICIPALITY MATCHING** - Use reference list above:
   - Story mentions "Cambridge" → That's DORCHESTER COUNTY
   - Story mentions "Easton" → That's TALBOT COUNTY
   - Story mentions "Salisbury" → That's WICOMICO COUNTY
   - Story mentions "Chestertown" → That's KENT COUNTY
   - Story mentions "Denton" → That's CAROLINE COUNTY

3. **DATELINE CHECK** - Beginning of article:
   - "CAMBRIDGE —" → Story is in DORCHESTER COUNTY
   - "EASTON —" → Story is in TALBOT COUNTY
   - "SALISBURY —" → Story is in WICOMICO COUNTY

FORMAT EXAMPLES (Use ACTUAL county names like these):
- Good: "Talbot County"
- Good: "Dorchester County; Talbot County" (if story covers multiple)
- Bad: "County 1; County 2"
- Bad: "the county"

⚠️ CRITICAL: "Talbot County", "Dorchester County" are FORMAT EXAMPLES showing the STYLE of county names to use.
DO NOT automatically use "Talbot County" or "Dorchester County" in your response.
Extract the ACTUAL county or counties that the article is about.
Use the real county names based on what municipalities or locations appear in the article text above.
Match municipalities to their counties using the reference list provided.

IMPORTANT: 
- Use the FULL county name: "Talbot County" not just "Talbot"
- If multiple counties mentioned, separate with semicolon: "Talbot County; Dorchester County"
- Only use "N/A" if absolutely NO Maryland location is mentioned

⚠️ Use SPECIFIC county names from the reference list above.

==========================================================================
TASK 5 - OTHER FIELDS
==========================================================================

content_type: Choose ONE:
news article, feature article, enterprise story, profile, analysis, sports story, arts/culture, opinion, obituary, calendar listing, legal notice, announcement, brief, other

importance_level: Rate 1-5
1=minor, 2=standard, 3=significant, 4=major, 5=critical

==========================================================================
RETURN JSON (NO MARKDOWN)
==========================================================================

{{
  "title": "{title}",
  "author": "FULL NAME (check beginning, end, everywhere)",
  "docref": "{docref}",
  "date": "{date}",
  "article_id": "ID or N/A",
  "year": "YYYY",
  "month": "MM",
  "day": "DD",
  "people": "Mayor John Smith; Rev. Maria Garcia; Dr. James Lee (EVERYONE quoted or mentioned)",
  "places": "Talbot County; Dorchester County (ACTUAL county names)",
  "organizations": "Talbot County Council; Easton High School; NAACP (ACTUAL organization names)",
  "content_type": "category",
  "importance_level": 1-5
}}

⚠️⚠️⚠️ CRITICAL WARNING - DO NOT COPY EXAMPLE NAMES ⚠️⚠️⚠️

The names shown above like "John Smith", "Maria Garcia", "James Lee", "Talbot County Council", "Easton High School" are PLACEHOLDER EXAMPLES showing the FORMAT ONLY.

DO NOT use these example names in your actual response.
EXTRACT THE REAL names, organizations, and counties from the article text.

EXAMPLES OF GOOD RESPONSES (using REAL data from article):
{{
  "people": "Mayor Robert Willey; Council Member Sarah Martinez; Rev. John Williams",
  "organizations": "Cambridge City Council; Dorchester County Public Schools; Eastern Shore NAACP",
  "places": "Dorchester County"
}}

EXAMPLES OF BAD RESPONSES (copying placeholder examples):
{{
  "people": "Mayor John Smith; Rev. Maria Garcia",
  "organizations": "Talbot County Council; Easton High School",
  "places": "Talbot County"
}}
^ DO NOT DO THIS unless those exact names actually appear in the article!

⚠️ REMEMBER: 
- Author and people are CRITICAL
- Use ACTUAL names from the article, not example placeholder names
- Use REAL organization names that appear in the article
- Use REAL county names based on locations mentioned in the article
- Only N/A after thorough search"""
    
    return prompt

def call_llm(prompt, model="groq/openai/gpt-oss-120b"):
    """Call llm CLI tool."""
    try:
        result = subprocess.run(
            ["llm", "-m", model, prompt],
            capture_output=True,
            text=True,
            check=True,
            timeout=120
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return None
    except subprocess.CalledProcessError as e:
        print(f"  ERROR: {e}")
        return None
    except FileNotFoundError:
        print("\nERROR: 'llm' command not found. Install: uv run llm install llm-groq")
        sys.exit(1)

def parse_response(response_text):
    """Parse LLM JSON response."""
    if not response_text:
        return None
    
    # Remove markdown if present
    if "```" in response_text:
        parts = response_text.split("```")
        if len(parts) >= 3:
            response_text = parts[1]
            if response_text.strip().startswith("json"):
                response_text = response_text.strip()[4:]
    
    try:
        return json.loads(response_text.strip())
    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        return None

def process_stories(input_file, output_file, model="groq/openai/gpt-oss-120b", limit=None):
    """Process stories with enhanced author/people extraction."""
    
    print(f"Loading stories from {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            stories = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: '{input_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}")
        sys.exit(1)
    
    total_stories = len(stories)
    if limit and limit < total_stories:
        stories = stories[:limit]
        print(f"Loaded {total_stories} stories, processing first {limit} (test mode)")
    else:
        print(f"Loaded {total_stories} stories")
    
    print(f"\n⚠️  ENHANCED VERSION: Focus on AUTHORS and PEOPLE\n")
    
    processed_stories = []
    errors = 0
    
    for i, story in enumerate(stories, 1):
        docref = story.get('docref', 'unknown')
        headline = story.get('headline', story.get('title', 'No headline'))
        
        print(f"[{i}/{len(stories)}] {docref}")
        print(f"  {headline[:65]}...")
        
        prompt = create_extraction_prompt(story)
        response = call_llm(prompt, model)
        
        if not response:
            print(f"  ERROR: No response")
            errors += 1
            processed_stories.append(story)
            continue
        
        data = parse_response(response)
        if not data:
            print(f"  ERROR: Parse failed")
            errors += 1
            processed_stories.append(story)
            continue
        
        # Add extracted fields
        story['title'] = data.get('title', headline)
        story['author'] = data.get('author', 'N/A')
        story['docref'] = data.get('docref', docref)
        story['date'] = data.get('date', story.get('date', 'N/A'))
        story['article_id'] = data.get('article_id', 'N/A')
        story['year'] = data.get('year', 'N/A')
        story['month'] = data.get('month', 'N/A')
        story['day'] = data.get('day', 'N/A')
        story['people'] = data.get('people', 'N/A')
        story['places'] = data.get('places', 'N/A')
        story['organizations'] = data.get('organizations', 'N/A')
        story['content_type'] = data.get('content_type', 'news article')
        story['importance_level'] = data.get('importance_level', 3)
        
        processed_stories.append(story)
        
        # Show what was found
        print(f"  ✓ Author: {story['author']}")
        print(f"  ✓ People: {story['people'][:70] if story['people'] != 'N/A' else 'N/A'}...")
        print(f"  ✓ Link: {story['docref']}")
        print()
    
    # Save
    print(f"Saving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_stories, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*70)
    print("COMPLETE")
    print("="*70)
    
    # Stats
    with_author = sum(1 for s in processed_stories if s.get('author', 'N/A') != 'N/A')
    with_people = sum(1 for s in processed_stories if s.get('people', 'N/A') != 'N/A')
    
    if limit and limit < total_stories:
        print(f"TEST MODE: Processed {len(processed_stories)} of {total_stories}")
    else:
        print(f"Stories processed: {len(processed_stories)}")
    
    print(f"Stories with authors: {with_author} ({with_author/len(processed_stories)*100:.1f}%)")
    print(f"Stories with people: {with_people} ({with_people/len(processed_stories)*100:.1f}%)")
    print(f"Errors: {errors}")
    print(f"Output: {output_file}\n")

def main():
    parser = argparse.ArgumentParser(description="Enhanced entity extraction (focus: authors & people)")
    parser.add_argument('--input', default='topic_stories.json', help='Input JSON file')
    parser.add_argument('--output', default=None, help='Output JSON file')
    parser.add_argument('--limit', type=int, default=None, help='Limit stories (for testing)')
    parser.add_argument('--version', default=None, help='Version suffix')
    parser.add_argument('--model', default='groq/openai/gpt-oss-120b', help='LLM model')
    
    args = parser.parse_args()
    
    # Generate output filename
    if args.output:
        output_file = args.output
    else:
        version = args.version if args.version else datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"stories_with_entities_v3_{version}.json"
    
    print("="*70)
    print("ENHANCED ENTITY EXTRACTION v3")
    print("Focus: AUTHORS & PEOPLE")
    print("="*70)
    print(f"Input:  {args.input}")
    print(f"Output: {output_file}")
    print(f"Model:  {args.model}")
    if args.limit:
        print(f"Limit:  {args.limit} stories (test mode)")
    print("="*70 + "\n")
    
    process_stories(args.input, output_file, args.model, args.limit)

if __name__ == "__main__":
    main()