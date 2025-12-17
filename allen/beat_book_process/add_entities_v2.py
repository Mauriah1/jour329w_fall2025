#!/usr/bin/env python3
"""
Extract standard entities from Star-Democrat race and diversity stories.
FIRST WITH topic_stories.json file THEN ONCE FINISH USE WEB SEARCH to find missing details (author, date, etc.)
Input: topic_stories.json (stories already about race/diversity)
Output: Race_stories_with_entities_websearch.json
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

def web_search_for_article(title, docref):
    """
    Search for article on Star-Democrat website to find additional context.
    Returns search results or None.
    """
    # Search for the article online
    search_query = f'site:stardem.com OR site:star-dem.com "{title}"'
    
    try:
        # Use perplexity for web search
        result = subprocess.run(
            ["llm", "-m", "perplexity/llama-3.1-sonar-large-128k-online", 
             f"Search for this article on the Star-Democrat website (stardem.com): '{title}'. "
             f"Find any additional information about: author name, exact publication date, people mentioned, organizations involved, location/county. "
             f"Return as JSON: {{\"author\": \"name if found\", \"date\": \"date if found\", \"additional_context\": \"any other relevant info found\"}}"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        
        # Parse the search result
        response = result.stdout.strip()
        if "```" in response:
            parts = response.split("```")
            if len(parts) >= 3:
                response = parts[1]
                if response.strip().startswith("json"):
                    response = response.strip()[4:]
        
        return json.loads(response.strip())
    except Exception as e:
        # Web search failed or not available
        print(f"    ⚠️  Web search failed: {str(e)[:50]}")
        return None

def create_extraction_prompt(story, web_search_enabled=False):
    """Create prompt for extracting entities with optional web search context."""
    
    title = story.get('headline', story.get('title', ''))
    text = story.get('context', story.get('text', ''))
    date = story.get('date', '')
    author = story.get('author', '')
    docref = story.get('docref', '')
    article_id = story.get('article_id', '')
    year = story.get('year', '')
    month = story.get('month', '')
    day = story.get('day', '')
    
    county_info = "\n".join([f"- {item['county']}: {item['municipalities']}" for item in maryland_county_list])
    
    # Try web search if enabled
    web_search_info = ""
    if web_search_enabled:
        print(f"    🔍 Searching web for additional context...")
        search_results = web_search_for_article(title, docref)
        if search_results:
            web_author = search_results.get('author', 'not found')
            web_date = search_results.get('date', 'not found')
            web_context = search_results.get('additional_context', 'not found')
            
            web_search_info = f"""
WEB SEARCH RESULTS FROM STAR-DEMOCRAT WEBSITE:
- Author found on website: {web_author}
- Date found on website: {web_date}
- Additional context: {web_context}

INSTRUCTIONS FOR USING WEB SEARCH RESULTS:
- If JSON has author but web search found different/additional author info, mention both or use most complete
- If JSON date differs from web date, use the more specific one
- Use web search context to enhance your understanding of people/organizations/locations
"""
            print(f"    ✓ Found web results")
        else:
            web_search_info = "\nWEB SEARCH: No results found or search unavailable.\n"
    
    prompt = f"""CRITICAL: Extract entities from this Star-Democrat article. You have TWO sources of information:

1. ARTICLE DATA FROM JSON (topic_stories.json) - PRIMARY SOURCE
2. WEB SEARCH RESULTS (from Star-Democrat website) - VERIFICATION/ENHANCEMENT

{web_search_info}

COUNTY REFERENCE:
{county_info}

ARTICLE METADATA FROM JSON (primary source - use these unless web search provides better info):
Title: {title}
Author: {author if author else '[Check web search]'}
Date: {date if date else '[Check web search]'}
Docref: {docref}
Article ID: {article_id if article_id else 'N/A'}
Year: {year if year else 'N/A'}
Month: {month if month else 'N/A'}
Day: {day if day else 'N/A'}

ARTICLE TEXT FROM JSON (extract people, organizations, counties from this):
{text}

YOUR TASK - Extract ONLY these 5 fields by reading the article text:

1. "people": ALL people mentioned (with titles), separated by ";"
   - Look in article text for names
   - Use web search context as additional reference
   - Format: "Title FirstName LastName; Title FirstName LastName"

2. "places": Maryland counties (use reference list), separated by ";"
   - Match cities/towns to counties using the reference list
   - Example: "Easton" → "Talbot County"

3. "organizations": ALL organizations mentioned, separated by ";"
   - Government, schools, nonprofits, businesses, churches
   - Use web search context as additional reference

4. "content_type": Choose ONE:
   - "news article", "feature article", "enterprise story", "profile"
   - "opinion", "brief", "other"

5. "importance_level": Rate 1-5
   - 1=minor, 2=standard, 3=significant, 4=major, 5=critical

IMPORTANT: 
- The metadata (title, author, date, etc.) from JSON will be used automatically by the script
- You ONLY need to return the 5 extracted fields
- DO NOT include title, author, date, docref, article_id, year, month, day in your response
- If web search provided useful context, use it to enhance your entity extraction

Return ONLY this JSON (no markdown, no explanations):
{{
  "people": "value or N/A",
  "places": "value or N/A",
  "organizations": "value or N/A",
  "content_type": "news article or other",
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

def process_stories(input_file, output_file, model="groq/openai/gpt-oss-120b", limit=None, web_search=False):
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
    
    if web_search:
        print(f"🔍 Web search ENABLED - will search Star-Democrat website for additional context\n")
    
    print(f"Processing {len(stories)} race/diversity stories...\n")
    
    processed_stories = []
    errors = 0
    
    for i, story in enumerate(stories, 1):
        docref = story.get('docref', 'unknown')
        headline = story.get('headline', story.get('title', 'No headline'))
        
        print(f"[{i}/{len(stories)}] {docref}")
        print(f"  {headline[:65]}...")
        
        # Create and call prompt
        prompt = create_extraction_prompt(story, web_search_enabled=web_search)
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
        
        # Use metadata DIRECTLY from JSON (not from LLM response)
        story['title'] = story.get('headline', story.get('title', 'N/A'))
        story['author'] = story.get('author', 'N/A')
        story['docref'] = story.get('docref', 'N/A')
        story['date'] = story.get('date', 'N/A')
        story['article_id'] = story.get('article_id', 'N/A')
        story['year'] = story.get('year', 'N/A')
        story['month'] = story.get('month', 'N/A')
        story['day'] = story.get('day', 'N/A')
        
        # Add entities extracted by LLM from article text (enhanced by web search if enabled)
        story['people'] = data.get('people', 'N/A')
        story['places'] = data.get('places', 'N/A')
        story['organizations'] = data.get('organizations', 'N/A')
        story['content_type'] = data.get('content_type', 'news article')
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
    print()

def main():
    """Main function with command-line argument support."""
    
    parser = argparse.ArgumentParser(
        description="Extract entities from Star-Democrat race/diversity stories (with optional web search)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all stories
  python add_entities_websearch.py
  
  # Test with first 5 stories
  python add_entities_websearch.py --limit 5
  
  # Enable web search for missing details
  python add_entities_websearch.py --limit 5 --web-search
  
  # Custom input/output files
  python add_entities_websearch.py --input my_stories.json --output my_output.json
        """
    )
    
    parser.add_argument(
        '--input',
        default='topic_stories.json',
        help='Input JSON file with stories (default: topic_stories.json)'
    )
    
    parser.add_argument(
        '--output',
        default='stories_with_entities_websearch.json',
        help='Output JSON file (default: stories_with_entities_websearch.json)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit number of stories to process (useful for testing)'
    )
    
    parser.add_argument(
        '--web-search',
        action='store_true',
        help='Enable web search on Star-Democrat website to enhance entity extraction with additional context (requires perplexity API)'
    )
    
    parser.add_argument(
        '--model',
        default='groq/openai/gpt-oss-120b',
        help='LLM model to use (default: groq/openai/gpt-oss-120b)'
    )
    
    args = parser.parse_args()
    
    # Print configuration
    print("="*70)
    print("STAR-DEMOCRAT ENTITY EXTRACTION (WITH WEB SEARCH)")
    print("="*70)
    print(f"Input:       {args.input}")
    print(f"Output:      {args.output}")
    print(f"Model:       {args.model}")
    print(f"Web Search:  {'ENABLED' if args.web_search else 'DISABLED'}")
    if args.limit:
        print(f"Limit:       Processing first {args.limit} stories only (testing mode)")
    else:
        print(f"Limit:       None (processing all stories)")
    print("="*70 + "\n")
    
    if args.web_search:
        print("⚠️  NOTE: Web search requires perplexity API.")
        print("    Install with: llm install llm-perplexity")
        print("    Set API key: llm keys set perplexity")
        print("    Web search will look for each article on Star-Democrat website.")
        print("    This provides additional context to enhance entity extraction.\n")
    
    if args.limit:
        print(f"⚠️  TEST MODE: Only processing {args.limit} stories\n")
    
    process_stories(args.input, args.output, args.model, limit=args.limit, web_search=args.web_search)

if __name__ == "__main__":
    main()