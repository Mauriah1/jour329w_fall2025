To get the top stories: 
uv run sqlite-utils memory data/tags.json "select * from tags order by count desc limit 20"
 The data is organized hierarchically with tags containing associated stories. Based on the count values, the most popular tags are Politics (156 stories), Education (134 stories),Health (89 stories), Environment (76 stories), Crime (65 stories) and Economy (58 stories)

Selected Tag: "budget cuts" (8 stories)
Tag URL: https://cnsmaryland.org/tag/budget-cuts/
Selected Story: "Moore's Blueprint Cuts Face Major Pushback"
URL: https://cnsmaryland.org/2025/02/21/moores-blueprint-cuts-face-major-pushback/
Title: Moore's Blueprint Cuts Face Major Pushback

Command ran:
 uv run python -m newspaper --url=https://cnsmaryland.org/2025/02/21/moores-blueprint-cuts-face-major-pushback/ -of=text | uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "You are an expert at categorizing topics for news stories. Read the text and provide no more than 5 topics."
 
 Response:[nltk_data] Downloading package punkt to /home/codespace/nltk_data...
[nltk_data]   Unzipping tokenizers/punkt.zip.
Traceback (most recent call last):
  File "/workspaces/jour329w_fall2025/.venv/lib/python3.12/site-packages/newspaper/nlp.py", line 202, in split_sentences
    tokenizer = split_sentences._tokenizer  # type: ignore[attr-defined]
                ^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'function' object has no attribute '_tokenizer'
During handling of the above exception, another exception occurred:
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/workspaces/jour329w_fall2025/.venv/lib/python3.12/site-packages/newspaper/__main__.py", line 12, in <module>
    main()
  File "/workspaces/jour329w_fall2025/.venv/lib/python3.12/site-packages/newspaper/cli.py", line 276, in main
    run(args)
  File "/workspaces/jour329w_fall2025/.venv/lib/python3.12/site-packages/newspaper/cli.py", line 239, in run
    article.nlp()
  File "/workspaces/jour329w_fall2025/.venv/lib/python3.12/site-packages/newspaper/article.py", line 608, in nlp
    summary_sents = nlp.summarize(
                    ^^^^^^^^^^^^^^
  File "/workspaces/jour329w_fall2025/.venv/lib/python3.12/site-packages/newspaper/nlp.py", line 71, in summarize
    sentences = split_sentences(text)
                ^^^^^^^^^^^^^^^^^^^^^
  File "/workspaces/jour329w_fall2025/.venv/lib/python3.12/site-packages/newspaper/nlp.py", line 215, in split_sentences
    tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspaces/jour329w_fall2025/.venv/lib/python3.12/site-packages/nltk/data.py", line 823, in load
    return switch_punkt(fil)
           ^^^^^^^^^^^^^^^^^
  File "/workspaces/jour329w_fall2025/.venv/lib/python3.12/site-packages/nltk/data.py", line 678, in switch_punkt
    return tok(lang)
           ^^^^^^^^^
  File "/workspaces/jour329w_fall2025/.venv/lib/python3.12/site-packages/nltk/tokenize/punkt.py", line 1744, in __init__
    self.load_lang(lang)
  File "/workspaces/jour329w_fall2025/.venv/lib/python3.12/site-packages/nltk/tokenize/punkt.py", line 1749, in load_lang
    lang_dir = find(f"tokenizers/punkt_tab/{lang}/")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspaces/jour329w_fall2025/.venv/lib/python3.12/site-packages/nltk/data.py", line 579, in find
    raise LookupError(resource_not_found)
LookupError: 
**********************************************************************
  Resource punkt_tab not found.
  Please use the NLTK Downloader to obtain the resource:
 >>> import nltk  >>> nltk.download('punkt_tab')
For more information see: https://www.nltk.org/data.html
 Attempted to load tokenizers/punkt_tab/english/
Searched in:
    - '/home/codespace/nltk_data'
    - '/workspaces/jour329w_fall2025/.venv/nltk_data'
    - '/workspaces/jour329w_fall2025/.venv/share/nltk_data'
    - '/workspaces/jour329w_fall2025/.venv/lib/nltk_data'
    - '/usr/share/nltk_data'
    - '/usr/local/share/nltk_data'
    - '/usr/lib/nltk_data'
    - '/usr/local/lib/nltk_data'
**********************************************************************
Sure, please provide the text you'd like me to analyze.

Then I knew I had to downlad punkt_tab:
@Mauriah1 ➜ /workspaces/jour329w_fall2025 (main) $ uv run python -c "import nltk; nltk.download('punkt_tab')"
[nltk_data] Downloading package punkt_tab to
[nltk_data]     /home/codespace/nltk_data...
[nltk_data]   Unzipping tokenizers/punkt_tab.zip.

After that I ran the piece of code again: 
uv run python -m newspaper --url=https://cnsmaryland.org/2025/02/21/moores-blueprint-cuts-face-major-pushback/ -of=text | uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "You are an expert at categorizing topics for news stories. Read the text and provide no more than 5 topics."

Output: 1. Maryland Blueprint for Maryland’s Future  
2. Education funding cuts / budget crisis  
3. Community schools & high-poverty grants  
4. Teacher collaborative-time delay / staffing shortage  
5. Partisan debate over taxes and spending

Those repsonds were more than two words so I then went back and added "uv run python -m newspaper --url=https://cnsmaryland.org/2025/02/21/moores-blueprint-cuts-face-major-pushback/ -of=text | uv run llm -m groq/moonshotai/kimi-k2-instruct-0905 "You are an expert at categorizing topics for news stories. Read the text and provide no more than 5 topics, however make the topics no more than two words."
Response: Education Funding, Budget Cuts, Community Schools, Teacher Shortage and Blueprint Reform. 

Overall, I felt like the tags that were provided from the llm matched up with some of the previously used CNS tags, so I thought that did a very well job. 



The process of troubleshooting this assignment was surprisingly engaging rather than frustrating. When the NLTK dependency issues emerged, the challenge required a very simple problem-solving approach (downloading the software). This wasn't a repetitiveverror it actually taught me something new about the web scraping ecosystem and how professional news sites protect their content. 

A better workflow for me for doing this cns tags creation would surround me controling the whole process. I'd design a more robust and user-friendly workflow. First, I'd create a CNS partnership that provides API access with full article content, eliminating scraping challenges entirely. The system would have a web interface where editors could paste article URLs or text, instantly see LLM-generated tag suggestions alongside existing CNS tags, and click to approve or modify suggestions. I'd also like to add confidence scores for each suggested tag based on frequency in the CNS archive, I just think that this would give people who arent that comfortable using llms a chance to compare. To me this system would feel less like debugging technical issues and more like having an AI assistant that truly understands CNS's editorial voice and reader needs.