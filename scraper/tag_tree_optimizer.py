# scraper/tag_tree_optimizer.py

def optimize_tag_tree(tag_tree):
    """
    Prunes and cleans the tag tree before sending to LLM.
    Removes empty nodes, limits depth and children count.
    """

    MAX_DEPTH = 8
    MAX_CHILDREN = 30
    MAX_TEXT_LEN = 150

    def prune(node, depth=0):
        if not isinstance(node, dict):
            return None

        # Stop at max depth
        if depth >= MAX_DEPTH:
            return {"tag": node.get("tag", "unknown"), "truncated": True}

        optimized = {}

        # Keep tag name
        if "tag" in node:
            optimized["tag"] = node["tag"]

        # Keep non-empty attrs only
        if "attrs" in node and node["attrs"]:
            optimized["attrs"] = node["attrs"]

        # Keep non-empty trimmed text only
        if "text" in node and node["text"] and node["text"].strip():
            optimized["text"] = node["text"].strip()[:MAX_TEXT_LEN]

        # Recursively prune children
        children = node.get("children", [])
        pruned_children = []
        for child in children[:MAX_CHILDREN]:
            pruned = prune(child, depth + 1)
            if pruned:
                pruned_children.append(pruned)

        if pruned_children:
            optimized["children"] = pruned_children

        return optimized if optimized else None

    # Handle both list and dict tag trees
    if isinstance(tag_tree, list):
        return [p for node in tag_tree if (p := prune(node))]
    elif isinstance(tag_tree, dict):
        return prune(tag_tree)
    else:
        return tag_tree