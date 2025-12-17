#!/usr/bin/env python3
"""
Extract standard entities from Star-Democrat race and diversity stories.
Input: topic_stories.json (stories already about race/diversity)
Output: stories_with_entities_1.json
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
    """Create prompt for extracting entities."""
    
    title = story.get('headline', story.get('title', ''))
    text = story.get('text', '')
    date = story.get('date', '')
    docref = story.get('docref', '')
    
    county_info = "\n".join([f"- {item['county']}: {item['municipalities']}" for item in maryland_county_list])
    
    prompt = f"""Extract entities from this news article about race and diversity.

COUNTY REFERENCE:
{county_info}

ARTICLE:
Title: {title}
Date: {date}
Docref: {docref}
Text: {text}

Extract and return ONLY valid JSON with these fields:

1. "title": Article title (from above)
2. "author": Author name if found in article (look for "By [Name]"), or "N/A"
3. "docref": Link/reference (from above)
4. "date": Publication date (from above)
5. "article_id": ID from docref if possible, or "N/A"
6. "year": Year from date
7. "month": Month from date
8. "day": Day from date
9. "people": Relevant people mentioned, separated by ";". Include politicians, community leaders, officials, quoted individuals. Use full names with titles. Or "N/A"
10. "places": Maryland counties where story takes place (use county list above), separated by ";". Or "N/A"
11. "organizations": Relevant organizations mentioned, separated by ";". Include government agencies, schools, nonprofits, businesses, community groups. Or "N/A"
12. "content_type": "full article" if it's a news article meant to inform (not calendar, obituary, opinion, listing), otherwise "other"
13. "importance_level": Rate 1-5:
    1 = Minor local story
    2 = Standard local news
    3 = Significant local story with community impact
    4 = Major story with regional importance
    5 = Critical story with broad implications

Return ONLY this JSON (no markdown):
{{
  "title": "value",
  "author": "value or N/A",
  "docref": "value",
  "date": "value",
  "article_id": "value or N/A",
  "year": "value",
  "month": "value",
  "day": "value",
  "people": "value or N/A",
  "places": "value or N/A",
  "organizations": "value or N/A",
  "content_type": "full article or other",
  "importance_level": 1-5
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
    """Process all stories (or limited number if specified)."""
    
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
            processed_stories.append(story)
            continue
        
        # Parse response
        data = parse_response(response)
        if not data:
            print(f"  ERROR: Failed to parse response")
            errors += 1
            processed_stories.append(story)
            continue
        
        # Add extracted fields to story
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
        story['content_type'] = data.get('content_type', 'full article')
        story['importance_level'] = data.get('importance_level', 3)
        
        processed_stories.append(story)
        
        print(f"  ✓ Author: {story['author']}")
        print(f"  ✓ Places: {story['places'][:50]}...")
        print(f"  ✓ Importance: {story['importance_level']}/5\n")
    
    # Save as JSON
    print(f"Saving {len(processed_stories)} stories to {output_file}...")
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
    print(f"\nNext steps:")
    if limit and limit < total_stories:
        print(f"  - Review the output: {output_file}")
        print(f"  - If results look good, run without --limit to process all stories")
    else:
        print(f"  - Load into Datasette for analysis")
        print(f"  - Document findings in notes.md")
    print()

def main():
    """Main function with command-line argument support."""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Extract entities from Star-Democrat race/diversity stories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all stories
  python stardem_entities_script_2.py
  
  # Test with first 5 stories
  python stardem_entities_script_2.py --limit 5
  
  # Process 10 stories with custom version
  python stardem_entities_script_2.py --limit 10 --version test1
  
  # Custom input/output files
  python stardem_entities_script_2.py --input my_stories.json --output my_output.json
        """
    )
    
    parser.add_argument(
        '--input',
        default='topic_stories.json',
        help='Input JSON file with stories (default: topic_stories.json)'
    )
    
    parser.add_argument(
        '--output',
        default=None,
        help='Output JSON file base name (default: stories_with_entities_1_vYYYYMMDD_HHMMSS.json)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit number of stories to process (useful for testing)'
    )
    
    parser.add_argument(
        '--version',
        default=None,
        help='Version suffix for output file (e.g., "test1", "final"). If not provided, uses timestamp.'
    )
    
    parser.add_argument(
        '--model',
        default='groq/openai/gpt-oss-120b',
        help='LLM model to use (default: groq/openai/gpt-oss-120b)'
    )
    
    args = parser.parse_args()
    
    # Determine output filename with versioning
    if args.output:
        output_file = args.output
    else:
        # Create versioned output filename
        if args.version:
            version_suffix = args.version
        else:
            # Use timestamp as version
            version_suffix = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        output_file = f"stories_with_entities_1_v{version_suffix}.json"
    
    # Print configuration
    print("="*70)
    print("STAR-DEMOCRAT ENTITY EXTRACTION")
    print("="*70)
    print(f"Input:   {args.input}")
    print(f"Output:  {output_file}")
    print(f"Model:   {args.model}")
    if args.limit:
        print(f"Limit:   Processing first {args.limit} stories only (testing mode)")
    else:
        print(f"Limit:   None (processing all stories)")
    print("="*70 + "\n")
    
    # Confirm if limiting
    if args.limit:
        print(f"⚠️  TEST MODE: Only processing {args.limit} stories\n")
    
    process_stories(args.input, output_file, args.model, limit=args.limit)

if __name__ == "__main__":
    main()