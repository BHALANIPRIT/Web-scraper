# services/data_analyser.py

import pandas as pd
import sys, os, urllib.request, json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


def _call_groq(prompt: str, system: str = "") -> str:
    """Groq API call — shared helper."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "[Error: GROQ_API_KEY not found in .env]"

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "llama-3.3-70b-versatile",
        "max_tokens": 1500,
        "messages": messages,
    }

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Groq API Error: {e}]"


def analyse_dataframe(df: pd.DataFrame, user_query: str = None) -> str:
    """DataFrame ko AI se analyse karo aur insights do."""
    summary = _build_summary(df)

    if user_query:
        prompt = f"""
You are a data analyst expert.

Dataset Summary:
{summary}

User Question: {user_query}

Answer the question clearly based on the data summary.
Be specific, concise, and use bullet points where helpful.
"""
    else:
        prompt = f"""
You are a data analyst expert.

Dataset Summary:
{summary}

Provide:
1. Key insights from this dataset
2. Patterns or trends you notice
3. Data quality observations
4. 3 recommended next steps for analysis

Be specific and concise.
"""
    return _call_groq(prompt, "You are a senior data analyst.")


def analyse_text_query(files_summary: str, user_query: str) -> str:
    """Global AI Assistant ke liye — multiple files ke baare mein query."""
    prompt = f"""
You are an AI assistant for a web scraping and data analysis platform.

Available Data Summary:
{files_summary}

User Question: {user_query}

Answer helpfully and concisely based on the available data.
"""
    return _call_groq(prompt, "You are a helpful data assistant.")


def _build_summary(df: pd.DataFrame) -> str:
    """DataFrame ka text summary banao LLM ke liye."""
    lines = [
        f"Rows: {df.shape[0]}, Columns: {df.shape[1]}",
        f"Column Names: {', '.join(df.columns.tolist())}",
        "",
        "Column Details:",
    ]

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            lines.append(
                f"  - {col} (numeric): min={df[col].min():.2f}, "
                f"max={df[col].max():.2f}, mean={df[col].mean():.2f}, "
                f"nulls={df[col].isna().sum()}"
            )
        else:
            top_vals = df[col].value_counts().head(3).index.tolist()
            lines.append(
                f"  - {col} (text): {df[col].nunique()} unique values, "
                f"top 3: {', '.join(str(v) for v in top_vals)}, "
                f"nulls={df[col].isna().sum()}"
            )

    lines.append("")
    lines.append("Sample Data (first 3 rows):")
    lines.append(df.head(3).to_string())

    return "\n".join(lines)