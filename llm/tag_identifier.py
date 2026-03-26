import json
from llm.llm_client import call_llm_api

def identify_target_tags(query):
    prompt = f"""
You are an expert in understanding web content structure.

User Query:
{query}

Task:
Based on the query, identify ALL POSSIBLE HTML TAGS that could contain the required data.

Rules:
1. Do NOT assume exact structure of a specific website.
2. Do NOT use attributes (class, id).
3. Return a BROAD but RELEVANT set of tags.
4. If query clearly refers to specific HTML elements, return those directly.
5. Otherwise, return a list of tags with highest probability.

Examples:

Query: "page title"
Output:
["title"]

Query: "all headings"
Output:
["h1", "h2", "h3", "h4", "h5", "h6"]

Query: "book names and prices"
Output:
["h1", "h2", "h3", "p", "span", "li", "a"]

Query: "table data"
Output:
["table", "tr", "td", "th"]

Query: "paragraph content"
Output:
["p", "div", "article", "section"]

STRICT:
- Return ONLY tag names
- DO NOT include attributes
- Return ONLY a JSON list of tag names.
"""

    response = call_llm_api(prompt)

    try:
        return json.loads(response)
    except:
        return []
