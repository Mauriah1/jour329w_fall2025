#!/usr/bin/env python3
"""
Extract standard entities from Star-Democrat race and diversity stories.
Input: topic_stories.json (stories already about race/diversity)
Output: race_and_diversity_finalv1.json
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
    """Create prompt for extracting entities with emphasis on people, orgs, places, and authors."""
    
    # Extract from the actual JSON structure in topic_stories.json
    title = story.get('headline', story.get('title', ''))
    context = story.get('context', story.get('text', ''))  # Article content is in 'context' field
    date = story.get('date', '')
    author =  story.get('author', '')
    docref = story.get('docref', '')
    article_id = story.get('article_id', '')
    year = story.get('year', '')
    month = story.get('month', '')
    day = story.get('day', '')
    
    county_info = "\n".join([f"- {item['county']}: {item['municipalities']}" for item in maryland_county_list])
    
    prompt = f"""CRITICAL: You are extracting entities from articles in topic_stories.json. This JSON file has a specific structure where article information is organized into fields.

IMPORTANT - UNDERSTANDING AUTHOR 
THE AUTHORS ARE IN THE TOPIC.JSON FILE UNDER AUTHOR RETURN ALL ATHORS, THIS IS A GIVEN AND IMPORTANT FUNCTION 

    
IMPORTANT - UNDERSTANDING THE JSON STRUCTURE:
The topic_stories.json file contains articles with these fields and this is the file you should use to get these fields DO NOT GENERATE FROM LLM but copy the data:
- "context": The full article text/content (this is where you'll find people, organizations, events)
- "date": The publication date (already extracted)
- "author": The article author is under author in topic_stories.json (already extracted)
- "headline" or "title": The article title (already extracted)
- "docref": Document reference ID (already extracted)
- "article_id": Article identifier (already extracted)
- "year": Publication year (already extracted)
- "month": Publication month (already extracted)
- "day": Publication day (already extracted)

YOUR TASK: Use ALL pre-extracted metadata (date, author, title, docref, article_id, year, month, day) AS PROVIDED. Only extract the following from the article CONTEXT: people, organizations, places (counties), content type, and importance level.

COUNTY REFERENCE - USE THIS TO IDENTIFY COUNTIES FROM THE ARTICLE:
{county_info}

ARTICLE INFORMATION FROM topic_stories.json:
---
Title: {title}
Author: {author}
Date: {date}
Docref: {docref}
Article ID: {article_id}
Year: {year}
Month: {month}
Day: {day}

ARTICLE CONTEXT (read carefully to find people, organizations, counties):
{context}
---

EXTRACTION REQUIREMENTS:

1. "title": **USE THE PROVIDED TITLE**
   Value: {title}
   (This is already extracted from the JSON - use it as-is)

2. "author": **USE THE PROVIDED AUTHOR**
   Value: {author}
   (This is already extracted from the JSON - use it as-is. This field should never be left empty as there is an authour to every story. if it is not under authour in the topic_stories.json it should be included in the context. 
3. "docref": **USE THE PROVIDED DOCREF**
   Value: {docref}
   (This is the document reference ID from the JSON)

4. "date": **USE THE PROVIDED DATE**
   Value: {date}
   (This is already extracted from the JSON - use it as-is)

5. "article_id": **USE THE PROVIDED ARTICLE ID**
   Value: {article_id}
   (This is already extracted from the JSON - use it as-is. If empty, use "N/A")

6. "year": **USE THE PROVIDED YEAR**
   Value: {year}
   (This is already extracted from the JSON - use it as-is. If empty, use "N/A")

7. "month": **USE THE PROVIDED MONTH**
   Value: {month}
   (This is already extracted from the JSON - use it as-is. If empty, use "N/A")

8. "day": **USE THE PROVIDED DAY**
   Value: {day}
   (This is already extracted from the JSON - use it as-is. If empty, use "N/A")

9. "people": **CRITICAL - READ THE ARTICLE CONTEXT CAREFULLY**
   Extract ALL people mentioned in the article context above. Look for:
   
   PEOPLE WITH TITLES:
   - Politicians: "Mayor John Smith", "Governor Jane Doe", "Councilman Bob Jones", "Delegate Mary White"
   - Officials: "Police Chief Tom Brown", "Superintendent Dr. Sarah Lee", "Director Mike Wilson"
   - Community leaders: "Rev. James Green", "Pastor Lisa Davis", "Imam Ahmed Hassan", "Rabbi David Cohen"
   - Activists: "Organizer Maria Rodriguez", "Advocate Kim Patel"
   - Professionals: "Dr. Robert Chen", "Attorney Jennifer White", "Professor Michael Jordan"
   - Business leaders: "CEO Amanda Mills", "President Chris Taylor"
   
   QUOTED PEOPLE (anyone who speaks in quotes MUST be included):
   - Look for quotation marks and the person who said it
   - "John Smith said...", "according to Jane Doe...", "Mary Wilson told reporters..."
   
    It should anybody in the context file that has a uppercase followed by a uppercase so for example : "Regina Hartfield" Would be a name of a person 
    Anytimes it says .. found or .. said it is usally a person 

   PEOPLE TAKING ACTIONS:
   - "John Smith voted...", "Jane Doe organized...", "Bob Jones announced..." "
   
   PEOPLE AFFECTED BY EVENTS:
   - Named residents, victims, participants, attendees, community members
   
   FORMAT: Separate with semicolons
   EXAMPLE: "Mayor John Smith; Dr. Sarah Johnson; Rev. James Williams; Council Member Maria Garcia"
   
   **DO NOT USE "N/A" UNLESS THERE ARE TRULY NO PEOPLE NAMED IN THE ARTICLE CONTEXT**

10. "places": **CRITICAL - IDENTIFY MARYLAND COUNTIES**
    Read the article context and identify which Maryland county/counties this story is about.
    Use the county reference list above to help match locations to counties.
    
    LOOK FOR:
    - Direct mentions: "Talbot County", "Dorchester County", "Caroline County", etc.
    - Municipality names: Use the reference list to match cities/towns to their counties
      * "Cambridge" → Dorchester County
      * "Easton" → Talbot County
      * "Denton" → Caroline County
      * "Chestertown" → Kent County
      * etc.
    - Datelines: "CAMBRIDGE - " suggests Dorchester County
    - Location phrases: "in Easton", "at Cambridge", "downtown Chestertown"
    
    FORMAT: Separate multiple counties with semicolons
    EXAMPLE: "Talbot County" or "Talbot County; Dorchester County"
    
    **This is important - the articles are from a Maryland Eastern Shore newspaper, so there should usually be a county. Only use "N/A" if truly no Maryland location is mentioned.**
    Also this is for any time any place is mentioned in the context file in the topic_stories.json file it should include any US or non U.S place, a place someone went to mention, somewhere the article is refrencing to, etc.. 

11. "organizations": **CRITICAL - IDENTIFY ALL ORGANIZATIONS**
    Read the article context and extract ALL organizations mentioned.
    
    GOVERNMENT & PUBLIC:
    - City/County councils: "Talbot County Council", "Easton Town Council"
    - School boards: "Talbot County Board of Education", "Caroline County Public Schools"
    - Police departments: "Cambridge Police Department", "Maryland State Police"
    - Government agencies: "Maryland Department of Health", "Dorchester County Government"
    
    SCHOOLS & EDUCATION:
    - K-12 schools: "Easton High School", "North Caroline High School"
    - Universities: "University of Maryland Eastern Shore", "Chesapeake College"
    
    NONPROFITS & COMMUNITY:
    - Advocacy groups: "NAACP", "Talbot County Free Library", "Dorchester County NAACP"
    - Churches: "Asbury United Methodist Church", "First Baptist Church"
    - Community centers: "Easton Family YMCA", "Boys and Girls Club"
    - Charities: "United Way", "Habitat for Humanity"
    
    BUSINESSES:
    - Named companies: "Perdue Farms", "Shore Regional Health"
    - Local businesses: specific named restaurants, shops, hospitals
    
    CULTURAL & CIVIC:
    - Museums: "Chesapeake Bay Maritime Museum", "Academy Art Museum"
    - Historical societies: "Talbot Historical Society"
    - Civic groups: "Rotary Club of Easton", "Talbot County Chamber of Commerce"
    
    FORMAT: Separate with semicolons
    EXAMPLE: "Talbot County Council; Easton High School; University of Maryland Eastern Shore; NAACP; Shore Regional Health"
    
    **DO NOT USE "N/A" UNLESS THERE ARE TRULY NO ORGANIZATIONS MENTIONED IN THE ARTICLE CONTEXT**

12. "content_type": **ANALYZE THE ARTICLE CONTEXT AND CLASSIFY**
    Read the article context carefully and determine what TYPE of content this is.
    
    Choose the SINGLE BEST match from these options:
    - "news article" = Standard news story reporting current events, government, community issues, breaking news
    - "feature article" = Longer, in-depth story with narrative elements, human interest, storytelling approach
    - "enterprise story" = Original investigative piece, exclusive reporting, deeply researched
    - "profile" = Story focused on a specific person, their life, work, or achievements
    - "analysis" = Explanatory piece providing context, interpretation, or implications (factual, not opinion)
    - "sports story" = Coverage of sports, games, athletes, teams, competitions
    - "arts/culture" = Coverage of arts, entertainment, cultural events, music, theater
    - "opinion" = Editorial, op-ed, columnist's views, letter to editor (expresses opinions)
    - "obituary" = Death notice, tribute to deceased person
    - "calendar listing" = Event listings, community calendar, upcoming activities
    - "legal notice" = Public notices, legal announcements, official postings
    - "announcement" = Brief public announcement, press release, notification
    - "brief" = Very short news item (typically under 200 words, minimal detail)
    - "other" = Doesn't fit any above category
    
    GUIDANCE: Most race/diversity stories will be:
    - "news article" if reporting on current events, policies, meetings, incidents
    - "feature article" if telling a longer story with narrative elements
    - "enterprise story" if original investigation or exclusive reporting
    - "profile" if focused on a specific person
    
    Choose ONE type that best fits the article.
    
13. "importance_level": **RATE THE STORY'S SIGNIFICANCE**
    Read the article context and rate its importance/impact on a scale of 1-5:
    
    - 1 = Minor local story (routine event, small announcement, brief update)
    - 2 = Standard local news (typical community story, regular coverage)
    - 3 = Significant local story (affects community, notable development, important issue)
    - 4 = Major story (regional importance, controversy, significant policy, strong public interest)
    - 5 = Critical story (major implications, breaking news, historic event, major policy change, widespread impact)
    
    Consider: Does this affect many people? Is it controversial? Is it a major policy? Is it breaking news?

IMPORTANT REMINDERS:
- Use the title, author, date, docref, article_id, year, month, and day exactly as provided from the JSON
- Read the ENTIRE article context to find people, organizations, and locations
- If someone is quoted, mentioned by name, or takes action in the story, include them in "people"
- Use the county reference list to match any mentioned city/town to its county
- List ALL organizations mentioned, referenced, or involved in the story
- Classify the content type based on the style and purpose of the article
- Only use "N/A" as a last resort when you've thoroughly checked and truly found nothing

Return ONLY valid JSON (no markdown, no code blocks, no explanations):
{{
  "title": "{title}",
  "author": "{author}",
  "docref": "{docref}",
  "date": "{date}",
  "article_id": "{article_id if article_id else 'N/A'}",
  "year": "{year if year else 'N/A'}",
  "month": "{month if month else 'N/A'}",
  "day": "{day if day else 'N/A'}",
  "people": "Person 1; Person 2; Person 3 (extract ALL from article context)",
  "places": "County 1; County 2 (identify from article context using reference list)",
  "organizations": "Org 1; Org 2; Org 3 (extract ALL from article context)",
  "content_type": "news article or feature article or enterprise story or profile or analysis or sports story or arts/culture or opinion or obituary or calendar listing or legal notice or announcement or brief or other",
  "importance_level": 1-5
}}"""
    
    return prompt

def call_llm(prompt, model="groq/meta-llama/llama-4-maverick-17b-128e-instruct"):
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
        # Use pre-extracted metadata from JSON
        story['title'] = data.get('title', headline)
        story['author'] = data.get('author', story.get('author', 'N/A'))  # Use extracted or original
        story['docref'] = data.get('docref', docref)
        story['date'] = data.get('date', story.get('date', 'N/A'))
        story['article_id'] = data.get('article_id', story.get('article_id', 'N/A'))  # Use original from JSON
        story['year'] = data.get('year', story.get('year', 'N/A'))  # Use original from JSON
        story['month'] = data.get('month', story.get('month', 'N/A'))  # Use original from JSON
        story['day'] = data.get('day', story.get('day', 'N/A'))  # Use original from JSON
        # Extract entities from article context
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
        default='race_and_diversity_finalv1.json',
        help='Output JSON file name (default: race_and_diversity_finalv1.json)'
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
        help='Version suffix for output file (e.g., "test1", "final"). Overrides default output filename.'
    )
    
    parser.add_argument(
        '--model',
        default='groq/openai/gpt-oss-120b',
        help='LLM model to use (default: groq/openai/gpt-oss-120b)'
    )
    
    args = parser.parse_args()
    
    # Determine output filename
    if args.version:
        # If version is specified, it overrides the default output
        output_file = f"stories_with_entities_v2_{args.version}.json"
    else:
        # Use the specified output or default
        output_file = args.output
    
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