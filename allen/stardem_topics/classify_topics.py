import json
import subprocess
import sys

# Your topic list
topic_list = [
    "Education",
    "Religion",
    "Animals",
    "Historical Information",
    "Sports",
    "Local Government",
    "Elections",
    "Courts and Public Safety",
    "Business and Economy",
    "Farming and Agriculture",
    "Other relevant Eastern Shore topics"
]

def classify_story(story):
    """Use LLM to classify a single story"""
    prompt = f"""Assign this news story to exactly ONE topic from the following list:

{', '.join(topic_list)}

Choose the topic that best represents what this story is primarily about.

Title: {story['title']}
Content: {story['content'][:500]}

Return only the topic name from the list above. Do not include any explanation or additional text."""
    
    # Call the llm command
    result = subprocess.run(
        ['uv', 'run', 'llm', '-m', 'groq/meta-llama/llama-4-scout-17b-16e-instruct', prompt],
        capture_output=True,
        text=True
    )
    
    topic = result.stdout.strip()
    return topic

def main():
    print("Loading stories from stardem_sample.json...")
    with open('stardem_sample.json', 'r') as f:
        stories = json.load(f)
    
    print(f"Found {len(stories)} stories to classify")
    print("Starting classification...\n")
    
    # Process each story
    for i, story in enumerate(stories, 1):
        print(f"Processing story {i}/{len(stories)}: {story['title'][:60]}...")
        topic = classify_story(story)
        story['topic'] = topic
        print(f"  → Assigned topic: {topic}\n")
    
    # Save results
    print("Saving results to stardem_topics_classified.json...")
    with open('stardem_topics_classified.json', 'w') as f:
        json.dump(stories, f, indent=2)
    
    print("Done! Classification complete.")

if __name__ == "__main__":
    main()
