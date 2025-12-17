When I started this assignment, I had one clear problem: my previous entity extraction attempts weren't working well. Articles were coming back with "N/A" for authors, incomplete lists of people mentioned, and missing organizations. I knew the information was there in my topic_stories.json file, I just needed to make the prompt in order to get the LLM to extract it properly. This is ultimately why I choose option 1.

I decided to create three different versions of my extraction script, each testing a different hypothesis about what would improve results. For all three versions, I used the same model—groq/openai/gpt-oss-120b—because I wanted to isolate the effect of my prompt engineering rather than comparing different AI models. Also from the previous assignment I liked the way this model ran the most. 

My first version focused on fixing a fundamental problem: I needed to make absolutely clear to the LLM where information was coming from. In previous assignments, I think I was confusing it by not explicitly stating that author, date, and title were already in the JSON file. This time, I restructured my prompt to say "USE these fields as-is" versus "EXTRACT these fields from the article text."

My hypothesis was simple: if I clearly separated what the LLM should use directly (metadata like author and date) from what it should extract (entities like people and organizations), I'd get better results. And I was right, authors started appearing consistently, dates were preserved correctly, and the overall accuracy jumped to around 70-80%. But I was still seeing incomplete people and organization lists, especially for articles that only had short excerpts in the JSON.

This is where things got interesting. I realized that even with perfect instructions, if an article's "context" field only contained a 50-word excerpt, the LLM couldn't find people and organizations that weren't mentioned in that excerpt. So I added to the prompt a web search capability. The script would search the Star-Democrat website for the full article, then use both the JSON data AND the web results to enhance extraction.

My hypothesis was that finding the full article online would give the LLM more context to work with. What I didn't expect was how dramatic the improvement would be. Suddenly, instead of finding 0-1 people per article, I was finding 3-5. Instead of 0 organizations, I was finding 1. The web search didn't just fill gaps, it transformed the quality of my extraction. This version became my clear winner.

For my third experiment, I went in a completely different direction. What if the problem wasn't missing data but too much complexity? I created a stripped-down version that only extracted seven essential fields: title, author, date, county, people, organizations, and docref. I also added a clever feature—the output would be sorted by completeness, with articles that had all six fields appearing first and articles with "N/A" values at the bottom.

My hypothesis was that simpler prompts with fewer fields would reduce confusion and improve accuracy per field. Ultimately this version was over-simplified, and the results that yielded were overly generic. It got the basic of who, what, when and where but no so much the why. 


Version 2, the web-enhanced extraction,was undoubtedly the best overall. When I compared outputs, the difference was striking. Let me give you an example:

Version 1 output:
"people": "Mayor"
"organizations": "City Council"

Version 2 output: 
"people": "Superintendent Dr. Sarah Lee; Rev. Michael Williams; Council Member Maria Garcia"
"organizations": "Talbot County Council; Board of Education; First Baptist Church; NAACP; University of Maryland Eastern Shore"

The web search version found more than twice as many entities. It wasn't just about quantity though, the quality improved too. With more context from the full article, the LLM could better understand who the key players were and which organizations were actually involved versus just mentioned in passing.

Looking at specific categories, Version 2 excelled everywhere, but especially with people and organizations. For places/counties, all three versions did reasonably well, probably because location information tends to be mentioned even in short excerpts. But for author, date, and title, all three versions were equally good because I'd fixed the fundamental problem in Version 1 of using JSON fields directly.

The consistency across versions was actually pretty good, which told me my prompt engineering was working. Authors, dates, and titles were nearly 100% consistent across all three versions. Places were shockingly similar as I noted during testing, whether I was working with full articles or excerpts, the LLM could identify counties. The main differences showed up in the completeness of people and organization lists, where having more text to work with (via web search) made all the difference.

One of my biggest discoveries was how much examples matter in prompts. When I just told the LLM "extract people," I got inconsistent results. But when I showed examples: "Politicians: 'Mayor John Doe', 'Governor Jane Smith'; Officials: 'Police Chief Tom Brown', 'Superintendent Dr. Sarah Lee'", suddenly the extraction became much more consistent and comprehensive.

The county reference list was another game changer. By providing a complete list of Maryland counties with their municipalities, the LLM could match "Easton" to "Talbot County" or "Cambridge" to "Dorchester County." Without this reference, I'd get back city names instead of counties, which wasn't what I wanted.

I also learned that instructions need to be very clear and specific. The prompts I spent the most time crafting, carefully explaining each category, providing examples, specifying formats—produced the best results. When I tried to be too brief or assumed the LLM would understand what I meant, mistakes crept in.

Interestingly, I found that complexity could work against me. When my prompt tried to extract more complicated fields with detailed instructions for each, the LLM sometimes got confused and dropped fields or mixed up categories. The simpler seven-field prompt in Version 3 showed me that sometimes less is more, howver yoy must be specfic so you wont get generic responses, the LLM did better when I asked it to focus on specific factors. 

A few things surprised me during this process. First, the web search feature was more valuable than I expected. I thought it would mainly help fill in missing authors or dates, but it turned out its real value was providing context for entity extraction. Even when the JSON already had an author and date, the web search made people and organization extraction far more complete.

Second, I discovered that sorting the output by completeness (Version 3's feature) was incredibly useful for quality control. Being able to immediately see that 87 articles had all six fields complete versus 4 articles with mostly N/A values gave me instant visibility into my data quality. This would be really valuable for a beat book—I could focus on the complete articles and flag the incomplete ones for follow-up research.

Third, I found two interesting patterns in my extracted data that I hadn't noticed before:
"Staff Writer" was the most commonly appearing author in the documents. Also Talbot County dominated the coverage, appearing in about 50% of all race and diversity articles. 

These patterns revealed something about my source material and the newspaper's coverage that I hadn't been aware of. It's the kind of insight that would be valuable to document in a beat book.

Something that I think is quite noticing is that the LLM made mistakes when my instructions weren't clear enough or when I asked it to do too many things at once. The LLM seemed to get confused by information overload.I also realized that even the best prompt can't extract information that isn't there. If an article excerpt is only 50 words and doesn't name any specific people, no amount of prompt engineering will magically produce those names. This is why the web search approach worked so well, it solved a data problem, not just a prompt problem.

My Recommendation for a Beat Book: If I were creating a beat book about race and diversity coverage this week, I would definitely use Version 2, the web-enhanced extraction with the Groq GPT-OSS-120b model combined with web search capability. There were fewer "N/A" values across all categories, multiple people identified per article, multiple organizations found and
better understanding of the full context of each story. 

For a beat book that I'd use long-term to understand coverage patterns and identify story opportunities, having complete, accurate data is crucial. The extra time and cost are worth the investment.

My recommended prompt structure would include: Clear explanation of the JSON file structure, the complete Maryland county reference list, specific categories with examples (politicians, officials, community leaders), explicit format requirements (use semicolons to separate, include titles with names) and instructions to use web search results to enhance extraction

Even with the web search version winning, there were still issues to address:
The "Staff Writer" problem: Many articles show "Staff Writer" instead of actual author names. This might be accurate, perhaps these articles genuinely didn't have individual bylines, but it's worth investigating whether the actual author names might be buried somewhere in the article text that I'm not capturing.

Entity name normalization: The LLM extracted "NAACP," "Talbot County NAACP," and "NAACP Talbot County" as separate organizations when they're really the same entity. For a beat book, I'd need to do post-processing to normalize these variations into canonical names.

Incomplete people extraction: Even with web search, some people are still being missed—particularly those mentioned without titles or in passing. This suggests I might need additional techniques like named entity recognition to catch everyone.

This assignment taught me that successful entity extraction is as much about understanding your data as it is about crafting good prompts. The web search approach worked because it solved a data problem (incomplete article text in JSON) rather than just a prompt problem. The best prompts in the world can't extract information that isn't there. I also learned that iteration and testing are crucial. Version 1 was good, Version 2 was better, and Version 3 taught me about the value of organization. Each experiment built on insights from the previous one. 

The --limit 5 flag became my best friend—being able to test with just five articles, refine my approach, and test again made the whole process manageable and cost-effective.

