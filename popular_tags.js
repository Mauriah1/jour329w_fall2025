// This file exports a function to get the top N popular tags from the tags.json data
async function getPopularTags(n = 5) {
    const response = await fetch('data/tags.json');
    if (!response.ok) throw new Error('Could not load tags.json');
    const tags = await response.json();
    return tags
        .filter(tag => tag.count > 0)
        .sort((a, b) => b.count - a.count)
        .slice(0, n);
}

// Example usage (for testing):
// getPopularTags(5).then(console.log);
