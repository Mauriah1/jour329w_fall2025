
#!/usr/bin/env python3
"""
Extract key fields from Star-Democrat race and diversity stories. FROM THE TOPIC.JSON FILE 
Focuses on: title, date, author, county, people, organizations, docref/link
Sorts results to show complete articles first, articles with N/A values last.

Input: topic_stories.json
Output: stories_sorted_by_completeness.json
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
    """Create prompt for extracting the 6 key fields."""
    
    title = story.get('headline', story.get('title', ''))
    text = story.get('context', story.get('text', ''))
    date = story.get('date', '')
    docref = story.get('docref', '')
    author = story.get('author', '')
    
    county_info = "\n".join([f"- {item['county']}: {item['municipalities']}" for item in maryland_county_list])
    
    prompt = f"""Extract key information from this Star-Democrat article.

COUNTY REFERENCE (use to identify Maryland counties):
{county_info}

ARTICLE INFORMATION:
Title: {title}
Date: {date}
Docref: {docref}

ARTICLE TEXT:
{text}

EXTRACT THESE 7 FIELDS:

1. "title": Use the provided title: {title}

2. "date": Use the provided date: {date}

3. "county": **CRITICAL - Identify Maryland county/counties**
   - Look for direct mentions: "Talbot County", "Dorchester County", etc.
   - Match cities/towns to counties using the reference list above
     Example: "Easton" → "Talbot County"
     Example: "Cambridge" → "Dorchester County"
   - Check datelines: "EASTON - " suggests Talbot County
   - If multiple counties, separate with "; "
   - ONLY use "N/A" if truly no Maryland location is mentioned

4. "people": **Extract ALL people mentioned in the article**
   - Include full names with titles
   - Politicians: "Mayor John Doe", "Councilman Bob Smith"
   - Officials: "Police Chief Sarah Lee", "Superintendent Dr. Mike Jones"
   - Community leaders: "Rev. James Green", "Pastor Lisa Davis"
   - Anyone quoted or taking action
   - Separate multiple people with "; "
   - Format: "Title FirstName LastName; Title FirstName LastName"
   - ONLY use "N/A" if no people are named in the article

5. "organizations": **Extract ALL organizations mentioned**
   - Government: "Talbot County Council", "Easton Police Department"
   - Schools: "Easton High School", "Caroline County Public Schools"
   - Nonprofits: "NAACP", "Boys and Girls Club"
   - Churches: "First Baptist Church", "Asbury United Methodist Church"
   - Businesses: Named companies, hospitals, etc.
   - Separate multiple organizations with "; "
   - ONLY use "N/A" if no organizations are mentioned

6. "docref": Use the provided docref: {docref}

7. IMPORTANT - UNDERSTANDING AUTHOR 
THE AUTHORS ARE IN THE TOPIC.JSON FILE UNDER AUTHOR RETURN ALL ATHORS, THIS IS A GIVEN AND IMPORTANT FUNCTION 

    
IMPORTANT - UNDERSTANDING THE JSON STRUCTURE:
The topic_stories.json file contains articles with these fields and this is the file you should use to get these fields DO NOT GENERATE FROM LLM but copy the data:
- "context": The full article text/content (this is where you'll find people, organizations, events)
- "date": The publication date (already extracted)
- "author": The article author is under author in topic_stories.json (already extracted)
- "title": The article title (already extracted)
- "docref": Document reference ID (already extracted)

IMPORTANT:
- Read the ENTIRE article carefully before extracting
- Look for people in quotes, taking actions, or being mentioned
- Match any city/town to its county using the reference list
- Include ALL organizations, not just the main ones
- Only use "N/A" when you've thoroughly checked and found nothing

Return ONLY valid JSON (no markdown, no code blocks, no explanations):
{{
  "title": "title",
  "date": "date",
  "county": "County Name or N/A",
  "people": "Person 1; Person 2; Person 3 or N/A",
  "organizations": "Org 1; Org 2; Org 3 or N/A",
  "docref": "docref"
  "Author": "author"
}}"""
    
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
        print("\nERROR: 'llm' command not found. Install: pip install llm")
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

def calculate_completeness_score(story):
    """
    Calculate how complete an article is (0-6 scale).
    6 = all fields have data
    0 = all fields are N/A
    """
    score = 0
    fields_to_check = ['title', 'date', 'county', 'people', 'organizations', 'docref']
    
    for field in fields_to_check:
        value = story.get(field, 'N/A')
        # Check if field has meaningful data (not N/A, not empty, not just whitespace)
        if value and value != 'N/A' and str(value).strip() and str(value).strip().lower() != 'n/a':
            score += 1
    
    return score

def process_stories(input_file, output_file, model="groq/openai/gpt-oss-120b", limit=None):
    """Process all stories and sort by completeness."""
    
    print(f"Loading stories from {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            stories = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: '{input_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in input file: {e}")
        sys.exit(1)
    
    # Apply limit if specified
    total_stories = len(stories)
    if limit and limit < total_stories:
        stories = stories[:limit]
        print(f"Loaded {total_stories} stories, processing first {limit} (test mode)")
    else:
        print(f"Loaded {total_stories} stories")
    
    print(f"Processing {len(stories)} race/diversity stories...\n")
    
    processed_stories = []
    errors = 0
    
    for i, story in enumerate(stories, 1):
        docref = story.get('docref', 'unknown')
        headline = story.get('headline', story.get('title', 'No headline'))
        
        print(f"[{i}/{len(stories)}] {docref}")
        print(f"  {headline[:65]}...")
        
        # Create and call prompt
        prompt = create_extraction_prompt(story)
        response = call_llm(prompt, model)
        
        if not response:
            print(f"  ERROR: No LLM response")
            errors += 1
            # Create minimal entry with N/A values
            processed_story = {
                'title': headline,
                'date': story.get('date', 'N/A'),
                'county': 'N/A',
                'people': 'N/A',
                'organizations': 'N/A',
                'docref': docref,
                'Author': story.get('author', '')
            }
            processed_stories.append(processed_story)
            continue
        
        # Parse response
        data = parse_response(response)
        if not data:
            print(f"  ERROR: Failed to parse response")
            errors += 1
            # Create minimal entry with N/A values
            processed_story = {
                'title': headline,
                'date': story.get('date', 'N/A'),
                'county': 'N/A',
                'people': 'N/A',
                'organizations': 'N/A',
                'docref': docref
            }
            processed_stories.append(processed_story)
            continue
        
        # Create new story with only the 6 fields
        processed_story = {
            'title': data.get('title', headline),
            'date': data.get('date', story.get('date', 'N/A')),
            'county': data.get('county', 'N/A'),
            'people': data.get('people', 'N/A'),
            'organizations': data.get('organizations', 'N/A'),
            'docref': data.get('docref', docref)
        }
        
        processed_stories.append(processed_story)
        
        # Calculate and show completeness
        score = calculate_completeness_score(processed_story)
        print(f"  ✓ County: {processed_story['county']}")
        print(f"  ✓ People: {processed_story['people'][:50]}...")
        print(f"  ✓ Completeness: {score}/6 fields\n")
    
    # Sort stories by completeness (most complete first)
    print("\n" + "="*70)
    print("SORTING BY COMPLETENESS")
    print("="*70)
    
    processed_stories.sort(key=lambda x: calculate_completeness_score(x), reverse=True)
    
    # Count by completeness level
    completeness_counts = {}
    for story in processed_stories:
        score = calculate_completeness_score(story)
        completeness_counts[score] = completeness_counts.get(score, 0) + 1
    
    print("Completeness distribution:")
    for score in sorted(completeness_counts.keys(), reverse=True):
        count = completeness_counts[score]
        print(f"  {score}/6 fields: {count} articles")
    
    # Save sorted JSON
    print(f"\nSaving {len(processed_stories)} stories to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_stories, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*70)
    print("COMPLETE")
    print("="*70)
    
    if limit and limit < total_stories:
        print(f"⚠️  TEST MODE RESULTS:")
        print(f"Processed: {len(processed_stories)} of {total_stories} total stories")
        print(f"Remaining: {total_stories - len(processed_stories)} stories not processed")
    else:
        print(f"Stories processed: {len(processed_stories)}")
    
    print(f"Errors: {errors}")
    print(f"Output saved to: {output_file}")
    print(f"\nSorting: Most complete articles first, articles with N/A values last")
    print(f"✓ Articles are sorted by completeness score (6/6 at top, 0/6 at bottom)")
    print()

def main():
    """Main function with command-line argument support."""
    
    parser = argparse.ArgumentParser(
        description="Extract 6 key fields and sort by completeness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Extracts 7 fields only:
  1. title
  2. date
  3. county (Maryland counties)
  4. people (all named individuals)
  5. organizations (all organizations)
  6. docref/link
  7. author 

Output is sorted so:
  - Complete articles (all 7 fields) appear FIRST
  - Articles with N/A values appear LAST
  - Sorted by completeness score (7/7 to 0/7)

Examples:
  # Process all stories
  python extract_and_sort.py
  
  # Test with first 5 stories
  python extract_and_sort.py --limit 5
  
  # Custom input/output files
  python extract_and_sort.py --input my_stories.json --output my_output.json
        """
    )
    
    parser.add_argument(
        '--input',
        default='topic_stories.json',
        help='Input JSON file with stories (default: topic_stories.json)'
    )
    
    parser.add_argument(
        '--output',
        default='stories_sorted_by_completeness.json',
        help='Output JSON file (default: stories_sorted_by_completeness.json)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit number of stories to process (useful for testing)'
    )
    
    parser.add_argument(
        '--model',
        default='groq/openai/gpt-oss-120b',
        help='LLM model to use (default: groq/openai/gpt-oss-120b)'
    )
    
    args = parser.parse_args()
    
    # Print configuration
    print("="*70)
    print("STAR-DEMOCRAT ENTITY EXTRACTION - 6 KEY FIELDS")
    print("="*70)
    print(f"Input:   {args.input}")
    print(f"Output:  {args.output}")
    print(f"Model:   {args.model}")
    if args.limit:
        print(f"Limit:   Processing first {args.limit} stories only (testing mode)")
    else:
        print(f"Limit:   None (processing all stories)")
    print("="*70)
    print("\nExtracting 6 fields:")
    print("  1. title")
    print("  2. date")
    print("  3. county")
    print("  4. people")
    print("  5. organizations")
    print("  6. docref/link")
    print("\nOutput will be sorted: Complete articles first, N/A values last")
    print("="*70 + "\n")
    
    if args.limit:
        print(f"⚠️  TEST MODE: Only processing {args.limit} stories\n")
    
    process_stories(args.input, args.output, args.model, limit=args.limit)

if __name__ == "__main__":
    main()