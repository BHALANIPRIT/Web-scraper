import json
from llm.groq_client import call_llm_api


def process_extracted_data(query, extracted_data):
    prompt = f"""
[SYSTEM: STRICT DATA MODE]
You are a specialized JSON generator. You do NOT speak. You do NOT explain.
Your output must START with '[' and END with ']'.  
  
User Query:
{query}

Extracted HTML Elements:
{json.dumps(extracted_data)[:12000]}

Task:
1. Identify relevant data from extracted content
2. Remove noise
3. Structure the output clearly
4. Maintain relationships (e.g., name-price pairs)

Return clean JSON or formatted answer.

STRICT:
- Do not hallucinate
- Use "Unknown" for any missing mandatory fields.
- Use only provided data

"""

    return call_llm_api(prompt)
