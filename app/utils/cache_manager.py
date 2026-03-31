import os
import json
import hashlib

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)


# 🔑 Generate stable filename from URL + query
def get_cache_key(url, query=None):
    key = url if not query else f"{url}_{query}"
    return hashlib.md5(key.encode()).hexdigest()


# 📥 Load cache (NO TTL — permanent)
def load_cache(url, query=None):
    key = get_cache_key(url, query)
    path = os.path.join(CACHE_DIR, f"{key}.json")

    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("content")
    except Exception:
        return None


# 📤 Save cache (overwrite if exists)
def save_cache(url, content, query=None):
    key = get_cache_key(url, query)
    path = os.path.join(CACHE_DIR, f"{key}.json")

    data = {
        "content": content
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)