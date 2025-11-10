#!/usr/bin/env python3
"""
Extract entities (people, places, organizations) from Star-Democrat stories.
"""

import json
import argparse
import llm

def extract_entities(story, model_name):
    """
    Extract people, places, and organizations from a story.
    
    Args:
        story: Dictionary containing story data with 'text' field
        model_name: Name of the LLM model to use
        
    Returns:
        Dictionary with extracted entities
    """
    
    # Create the prompt with an example
    prompt = f"""Extract all people, places, and organizations mentioned in this news article.

Example:
Article: "Governor Sarah Johnson visited Baltimore yesterday to meet with Mayor Tom Davis at City Hall. They discussed new policies with representatives from the Maryland Chamber of Commerce."

Output:
{{
  "people": ["Sarah Johnson", "Tom Davis"],
  "places": ["Baltimore", "City Hall"],
  "organizations": ["Maryland Chamber of Commerce"]
}}

Now extract entities from this article:

{story.get('text', '')}

Return only valid JSON with three arrays: "people", "places", and "organizations". Include only the most important and clearly mentioned entities. Use proper capitalization. Return empty arrays if no entities of that type are found."""

    try:
        model = llm.get_model(model_name)
        response = model.prompt(prompt)
        result = response.text().strip()
        
        # Try to parse the JSON response
        # Sometimes the model includes markdown code blocks, so let's handle that
        if result.startswith("```"):
            # Remove markdown code blocks
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
        description="Extract entities from Star-Democrat stories"
    )
    parser.add_argument(
        "--model",
        required=True,
        help="LLM model to use (e.g., groq/meta-llama/llama-4-maverick-17b-128e-instruct)"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input JSON file with stories"
    )
    parser.add_argument(
        "--output",
        default="stories_with_entities.json",
        help="Output JSON file (default: stories_with_entities.json)"
    )
    
    args = parser.parse_args()
    
    print(f"Loading stories from {args.input}...")
    with open(args.input, 'r') as f:
        stories = json.load(f)
    
    print(f"Processing {len(stories)} stories with model {args.model}...")
    
    processed_stories = []
    for i, story in enumerate(stories, 1):
        print(f"Processing story {i}/{len(stories)}: {story.get('docref', 'unknown')}")
        
        # Extract entities
        entities = extract_entities(story, args.model)
        
        # Add entities to story
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