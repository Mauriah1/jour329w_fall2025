CNS Metadata 09/27/25
Pre code : 
@Mauriah1 ➜ /workspaces/jour329w_fall2025 (main) $ git fetch upstream
git merge upstream/main
@Mauriah1 ➜ /workspaces/jour329w_fall2025 (main) $ cd allen
@Mauriah1 ➜ /workspaces/jour329w_fall2025/allen (main) $ mkdir cns_metadata
@Mauriah1 ➜ /workspaces/jour329w_fall2025/allen (main) $ cd cns_metadata
@Mauriah1 ➜ /workspaces/jour329w_fall2025/allen/cns_metadata (main) $ touch notes.md
@Mauriah1 ➜ /workspaces/jour329w_fall2025/allen/cns_metadata (main) $ cd .. 
@Mauriah1 ➜ /workspaces/jour329w_fall2025/allen (main) $ cd ..
@Mauriah1 ➜ /workspaces/jour329w_fall2025 (main) $ uv run llm keys set anthropic
Enter key: 
####
Assignment:
Gov. Moore’s proposed budget features massive cuts and tax hikes (https://cnsmaryland.org/2025/01/15/gov-moores-proposed-budget-features-tax-reform-and-massive-cuts/) 
My version: 
up to 3 key people (with title or role) :  Governor Wes Moore and Maryland residents. 
up to 3 main organizations/institutions : Governor Wes Moore adminstartion, The Republicans House of representatives and the Senate.
up to 3 geographic locations : Maryland
3 short (two-word) topics you would assign : Budject Cuts, Problematic, Maryland State.  
what kind of story is this - breaking news, feature, analysis, investigation, other : Feature Story 
a rating of the story's importance on a scale from 1 to 5, taking into account its impact on people (greater impact means higher score): 5 
(code: uv run python -m newspaper --url=https://cnsmaryland.org/2025/01/15/gov-moores-proposed-budget-features-tax-reform-and-massive-cuts/ -of=text | uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "Extract structured metadata from this news story and return as JSON with these exact fields:)
The llm answer : "people": ["Gov. Wes Moore", "House Republican Leader Jason Buckel", "Senate Republican Leader Stephen Hershey Jr."],
  "organizations": ["Maryland General Assembly", "Department of Budget and Management", "Developmental Disabilities Administration"],
  "locations": ["Annapolis", "Allegany County", "Caroline County", "Cecil County", "Kent County", "Queen Anne’s County", "Baltimore County", "Baltimore City"],
  "topics": ["budget", "taxes", "education", "deficit", "cuts"],
  "story_type": "breaking news",
  "impact": 4


Officials warn Pentagon cuts could force closing of Bethesda military medical university (https://cnsmaryland.org/2019/11/20/officials-warn-pentagon-cuts-could-force-closing-of-bethesda-military-medical-university/)
up to 3 key people (with title or role): Secretary of Defense Mark Esper and other senior leaders within the DoD, All of the seniors in the Military’s Medical School and Von Holler
up to 3 main organizations/institutions : The Department of Defense, The Military’s Medical School, and Democrats. 
up to 3 geographic locations : Bethesda, Maryland
3 short (two-word) topics you would assign: Problematic, Budjet Cuts, Dod
what kind of story is this - breaking news, feature, analys: investigative 
a rating of the story's importance on a scale from 1 to 5, taking into account its impact on people (greater impact means higher score): 4
(code:uv run python -m newspaper --url=https://cnsmaryland.org/2019/11/20/officials-warn-pentagon-cuts-could-force-closing-of-bethesda-military-medical-university/ -of=text | uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "Extract structured metadata from this news story and return as JSON with these exact fields: )
The llm answer: "people": ["Sen. Chris Van Hollen (D-Maryland)", "Richard Thomas (President, USU)", "Mark Esper (Secretary of Defense)"],
  "organizations": ["Defense Department", "Uniformed Services University of the Health Sciences", "Capital News Service"],
  "locations": ["Bethesda, Maryland", "Washington"],
  "topics": ["budget cuts", "military medicine", "university closure"],
  "story_type": "breaking news",
  "impact": 4


Van Hollen, Democratic Leaders Urge Rejection of Proposed Republican Budget (https://cnsmaryland.org/2015/03/25/van-hollen-democratic-leaders-urge-rejection-of-proposed-republican-budget/)
up to 3 key people (with title or role) : Von hollen and The House and Senate Democrats and The House and Senate Republicans. 
up to 3 main organizations/institutions: House and Senate Democrats and Republicans. 
up to 3 geographic locations : Washington D.C. 
3 short (two-word) topics you would assign : Budjet Cuts, Von Hollen, and Health Care. 
what kind of story is this - breaking news, feature, analysis, investigation, other : Feature 
a rating of the story's importance on a scale from 1 to 5, taking into account its impact on people (greater impact means higher score) : 4
(code:  uv run python -m newspaper --url=https://cnsmaryland.org/2015/03/25/van-hollen-democratic-leaders-urge-rejection-of-proposed-republican-budget/ -of=text | uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "Extract structured metadata from this news story and return as JSON with these exact fields: )
The llm answer :  "people": [
    "Rep. Chris Van Hollen, D-Md., Ranking Member House Budget Committee",
    "Sen. Bernie Sanders, I-Vt., Senate Budget Committee Ranking Member",
    "Rep. Andy Harris, R-Md."
  ],
  "organizations": [
    "House Budget Committee",
    "Senate Budget Committee",
    "Alzheimer’s Association"
  ],
  "locations": [
    "Washington",
    "Kensington",
    "Cockeysville",
    "Maryland",
    "Vermont",
    "Illinois"
  ],
  "topics": [
    "Republican budget",
    "healthcare cuts",
    "Medicaid",
    "Medicare",
    "tax breaks"
  ],
  "story_type": "other",
  "impact": 4

In First State of the State Address, Hogan Emphasizes Business, Tax Cuts (https://cnsmaryland.org/2015/02/04/in-first-state-of-the-state-address-hogan-emphasizes-business-tax-cuts/)
My version: 
up to 3 key people (with title or role) : Larry Hogan and The Senate 
up to 3 main organizations/institutions : Govern Larry Hogan's administration and the Senate 
up to 3 geographic locations : Maryland 
3 short (two-word) topics you would assign : Budjet Cuts, Larry Hogan, and problematic. 
what kind of story is this - breaking news, feature, analysis, investigation, other : feature story 
a rating of the story's importance on a scale from 1 to 5, taking into account its impact on people (greater impact means higher score) : 3
(code :  un run python -m newspaper --url=https://cnsmaryland.org/2015/02/04/in-first-state-of-the-state-address-hogan-emphasizes-business-tax-cuts/ -of=text | uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "Extract structured metadata from this news story and return as JSON with these exact fields:)
(code:uv run python -m newspaper --url=https://cnsmaryland.org/2015/02/04/in-first-state-of-the-state-address-hogan-emphasizes-business-tax-cuts/ -of=text | uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "Extract structured metadata from this news story and return as JSON with these exact fields:)
The llm answer : "people": [
    "Larry Hogan – Governor of Maryland",
    "Thomas V. “Mike” Miller Jr. – President, Maryland State Senate",
    "J.B. Jennings – Senate Minority Leader, Maryland"
  ],
  "organizations": [
    "Maryland General Assembly",
    "Maryland Republican Party",
    "Maryland Democratic Party"
  ],
  "locations": [
    "Annapolis, MD",
    "Maryland",
    "Calvert County, MD",
    "Charles County, MD",
    "Prince George’s County, MD",
    "Baltimore, MD",
    "Harford County, MD",
    "Caroline County, MD",
    "Dorchester County, MD",
    "Talbot County, MD",
    "Wicomico County, MD",
    "Howard County, MD",
    "Anne Arundel County, MD",
    "Chesapeake Bay",
    "Conowingo Dam",
    "Susquehanna River"
  ],
  "topics": [
    "tax cuts",
    "business climate",
    "rain tax repeal",
    "charter schools",
    "heroin epidemic"
  ],
  "story_type": "other",
  "impact": 4

How sequestration will impact Maryland and national party politics (https://cnsmaryland.org/2013/02/28/how-sequestration-will-impact-maryland-and-national-party-politics/)
up to 3 key people (with title or role) : Congressional leaders and the White House 
up to 3 main organizations/institutions : Congress and The White House 
up to 3 geographic locations : Washington D.C
3 short (two-word) topics you would assign : Budjet Cuts, The White House and problematic 
what kind of story is this - breaking news, feature, analysis, investigation, other : feature story 
a rating of the story's importance on a scale from 1 to 5, taking into account its impact on people (greater impact means higher score) : 5 
(code:uv run python -m newspaper --url=https://cnsmaryland.org/2013/02/28/how-sequestration-will-impact-maryland-and-national-party-politics/ -of=text | uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "Extract structured metadata from this news story and return as JSON with these exact fields:)
The llm answer: "people": ["Don Kettl, dean of the University of Maryland School of Public Policy"],
  "organizations": ["White House", "Congress", "Defense Department", "University of Maryland School of Public Policy"],
  "locations": ["Maryland", "Washington"],
  "topics": ["sequestration", "budget cuts", "federal workers", "defense", "Tea Party"],
  "story_type": "breaking news",
  "impact": 4
}

Evaluation Summary
The LLM-generated metadata consistently outperformed my human responses across all five news stories, demonstrating superior specificity, accuracy, and comprehensiveness. My key human weaknesses included persistent overly generic categorizations ("Maryland residents" vs specific officials), and vague topic descriptors like "problematic." The LLMs provided precise official titles, comprehensive geographic coverage including specific counties and cities, and policy-specific topic identification. However, I occasionally showed better contextual understanding, particularly with impact ratings where the human assessment of sequestration's significance (rating: 5) was more accurate than the LLM's lower rating (4).

Some of the changes that I could put into the command line to make this easier and to produce more conistent answers would be to combind all of the links, as this would save a lot of time and produce answers that would be in the same format. I actually tried this and I ran into some errors, however when I run this on the claude actual platform, I got no errors.

Scaling this process to 50-500 stories would face significant challenges as my intention spand already started to wander, but this would also make it alot harder to compare all of the response. To make the comparison and revision easier, implementing structured workflow tools, version control for prompt evolution, and automated comparison scripts would be very essential. If i wanted to present this work to others, I would need to create executive dashboards with accuracy metrics. The enhanced prompt structure would include specific formatting requirements, clearer field definitions, and validation commands to check for spelling accuracy and content completeness.