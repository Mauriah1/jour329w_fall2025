# Copilot Conversation Summary: StarDem Nearly Final Project

**Date:** December 16, 2025

## Project Overview

The `stardem_nearly_final` folder contains the culmination of work on a Beat Book project focused on the Maryland Eastern Shore, specifically addressing race and diversity coverage. This represents one of the most refined iterations of an AI-assisted reporter's guide generator that synthesizes story data and provides actionable journalism resources.

## Project Components

### Core Files
1. **notes.md** - Project retrospective and lessons learned
2. **prompt.txt** - Python script for generating reporter guides from JSON story data
3. **important_people_organizations.md** - Reference document of key sources mentioned 3+ times in coverage
4. **reporter_guide_county.md** - Generated output guide organized by county
5. **source_stories_final.json** - Source data containing story information

## Key Accomplishments & Evolution

### Previous Iterations
The user completed multiple versions of this beat book project (tracked through versions like `stardem_choice`, `stardem_draft`, `stardem_draft2`, `stardem_draft3`, `stardem_entities`, `stardem_topic_entities`, and `stardem_topics`). Each iteration refined the approach and added new capabilities.

### Nearly Final Version - Key Improvements
The `nearly_final` version represents a significant leap forward with several deliberately designed enhancements:

**1. Removed Quick Stats Box**
- Previous versions included a statistics box that provided little journalistic value
- This was eliminated in favor of more substantive content

**2. Enhanced County-by-County Breakdown**
- Narrowed focus to only selected counties as specified by the user
- Restructured output from bullet points/tables to **narrative paragraphs** for better readability
- Provides context and connections rather than isolated facts

**3. Improved Terminology Recommendations**
- Previous versions used overly generic recommended terminology
- Updated to provide **journalist-specific, actionable language** that would be useful in actual reporting
- However, the user noted this section still required work and was ultimately removed

**4. Important People & Organizations Reference**
- Created a curated list of key figures mentioned 3+ times in coverage
- Includes people like Carl Snowden, Victoria Gomez Lozano, and others with specific context on why they're important
- Ensures AI doesn't fabricate sources but draws from verified story data

## Quality Assessment

### Strengths of This Version
- **Narrative flow**: Guide reads as connected prose rather than lists
- **Source quality**: Provided sources are accurate and relevant (not fabricated)
- **Journalist-focused**: Sections like "Potentially Sensitive Topics" provide practical guidance for reporters
- **Geographic organization**: County-by-county breakdown is comprehensive and well-structured

### Areas Requiring Refinement
- **Source redundancy**: The same sources appear both in general sections and county breakdowns—identified as repetitive
- **Generic terminology**: Despite improvements, some terminology recommendations remained too generic; this section was ultimately removed
- **Source placement accuracy**: While no sources were fabricated, some people and organizations appeared in incorrect county or thematic placements during fact-checking

## Methodology

The project uses a two-pass extraction and synthesis approach:

1. **First Pass**: Extracts essential information from story data (title, headline, date, source, key content)
2. **Second Pass**: Synthesizes information into thematic and geographic summaries using LLM guidance

**Critical Constraint**: "Only use story info - NO fabrication" is enforced throughout the process.

## Key People & Organizations Identified

The reference document identifies important regional figures including:
- **Carl Snowden** - Civil rights organizer and spokesperson
- **Victoria Gomez Lozano** - Hispanic/Latino community representative
- **Tina Jones & Kyle O'Donnell** - LGBTQ+ community leadership (Delmarva Pride Center)
- **Matthew Peters** - Chesapeake Multicultural Resource Center director
- **Jaelon Moaney** - Maryland Commission on African American History and Culture
- **Dave Stepp & Keasha Haythe** - Talbot County Council (representing opposing DEI positions)
- **Lajan Cephas** - Cambridge Mayor

## User's Satisfaction & Decisions

The user expressed **high satisfaction** with this version, noting it as "one of the best versions thus far." Key decision-making moments:

1. **Kept the county narratives** - This format proved most effective
2. **Removed generic terminology section** - Decided this didn't serve journalism needs
3. **Accepted source duplication issue** - Identified for future refinement but acceptable in current form
4. **Verified accuracy** - Conducted fact-checking and confirmed no fabricated sources

## Next Steps for Future Iterations

Based on the notes, potential improvements for subsequent versions would include:
- Eliminate redundant source citations between general content and county sections
- Refine terminology section to be more specific and actionable for journalists
- Continue geographic accuracy refinement through fact-checking
- Consider expanding reference documents for other demographic angles

## Technical Notes

The project relies on:
- LLM integration via Python `llm` library
- JSON source data processing
- Reference document context injection for accuracy
- Batch processing of stories for scalability

## Conclusion

The `stardem_nearly_final` version represents a mature approach to AI-assisted beat book generation, balancing automation with journalistic integrity. The strong emphasis on narrative prose, geographic organization, and verified sources makes this a practical tool for reporters covering Eastern Shore race and diversity issues. The identified refinements point toward an even stronger final version.
