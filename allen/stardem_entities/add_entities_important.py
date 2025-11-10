#!/usr/bin/env python3
"""
Extract IMPORTANT entities (people, places, organizations) from Star-Democrat stories.
This version focuses on key entities only, not every mention.
"""

import json
import argparse
import llm

def extract_entities(story, model_name):
    """
    Extract important people, places, and organizations from a story.
    
    Args:
        story: Dictionary containing story data with 'text' field
        model_name: Name of the LLM model to use
        
    Returns:
        Dictionary with extracted entities
    """
    
    # Modified prompt focusing on IMPORTANT entities only
    prompt = f"""Extract only the MOST IMPORTANT people, places, and organizations from this news article. 

Focus on:
- People: Named individuals who are central to the story (officials, key figures who take action or are quoted)
- Places: Specific locations that are central to the story (cities, specific venues, landmarks - not general regions)
- Organizations: Formal organizations, companies, government bodies that play a key role in the story

Example:
Article: "Governor Sarah Johnson visited Baltimore yesterday to meet with Mayor Tom Davis at City Hall. They discussed new policies with representatives from the Maryland Chamber of Commerce. The meeting was attended by several residents from the Eastern Shore region."

Output:
{{
  "people": ["Sarah Johnson", "Tom Davis"],
  "places": ["Baltimore", "City Hall"],
  "organizations": ["Maryland Chamber of Commerce"]
}}

Note: "Eastern Shore region" was not included because it's a general area, not a specific central location.

Now extract the MOST IMPORTANT entities from this article:

{story.get('text', '')}

Return only valid JSON with three arrays: "people", "places", and "organizations". Include ONLY entities that are central to the story's main point. Use proper capitalization. Limit to the 5-7 most important entities per category. Return empty arrays if no important entities of that type are found."""

    try:
        model = llm.get_model(model_name)
        response = model.prompt(prompt)
        result = response.text().strip()
        
        # Try to parse the JSON response
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
            result = result.strip()
        
        entities = json.loads(result)
        
        # Validate structure
        if not all(key in entities for key in ["people", "places", "organizations"]):
            print(f"Warning: Missing keys in response for docref {story.get('docref', 'unknown')}")
            return {
                "people": entities.get("people", []),
                "places": entities.get("places", []),
                "organizations": entities.get("organizations", [])
            }
        
        return entities
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for docref {story.get('docref', 'unknown')}: {e}")
        print(f"Response was: {result[:200]}")
        return {
            "people": [],
            "places": [],
            "organizations": []
        }
    except Exception as e:
        print(f"Error processing docref {story.get('docref', 'unknown')}: {e}")
        return {
            "people": [],
            "places": [],
            "organizations": []
        }

def main():
    parser = argparse.ArgumentParser(
        description="Extract IMPORTANT entities from Star-Democrat stories"
    )
    parser.add_argument(
        "--model",
        required=True,
        help="LLM model to use"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input JSON file with stories"
    )
    parser.add_argument(
        "--output",
        default="stories_with_entities_important.json",
        help="Output JSON file (default: stories_with_entities_important.json)"
    )
    
    args = parser.parse_args()
    
    print(f"Loading stories from {args.input}...")
    with open(args.input, 'r') as f:
        stories = json.load(f)
    
    print(f"Processing {len(stories)} stories with model {args.model}...")
    print("Using IMPORTANT ENTITIES ONLY prompt")
    
    processed_stories = []
    for i, story in enumerate(stories, 1):
        print(f"Processing story {i}/{len(stories)}: {story.get('docref', 'unknown')}")
        
        entities = extract_entities(story, args.model)
        
        story_with_entities = story.copy()
        story_with_entities['people'] = entities['people']
        story_with_entities['places'] = entities['places']
        story_with_entities['organizations'] = entities['organizations']
        
        processed_stories.append(story_with_entities)
    
    print(f"\nSaving results to {args.output}...")
    with open(args.output, 'w') as f:
        json.dump(processed_stories, f, indent=2)
    
    print("Done!")
    
    # Print summary statistics
    total_people = sum(len(s.get('people', [])) for s in processed_stories)
    total_places = sum(len(s.get('places', [])) for s in processed_stories)
    total_orgs = sum(len(s.get('organizations', [])) for s in processed_stories)
    
    print(f"\nSummary:")
    print(f"  Total people: {total_people}")
    print(f"  Total places: {total_places}")
    print(f"  Total organizations: {total_orgs}")
    print(f"  Average entities per story: {(total_people + total_places + total_orgs) / len(processed_stories):.2f}")

if __name__ == "__main__":
    main()