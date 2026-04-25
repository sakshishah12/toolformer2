import random
import re
from tools.legal import statute_lookup, law_lookup, date_calculator,courtlistener_search

TOOLS = ["CaseLawSearch", "StatuteLookup", "LawLookup", "DateCalculator"]


# --- Simple heuristics (you can improve later) ---
def detect_tool(text):
    t = text.lower()

    if " v." in t:
        return "CaseLawSearch"

    if "u.s.c" in t or "§" in t:
        return "StatuteLookup"

    if "public law" in t:
        return "LawLookup"

    if re.search(r"\d{4}-\d{2}-\d{2}", text):
        return "DateCalculator"

    return None


# --- Generate tool call string ---
def build_tool_call(tool, text):
    if tool == "CaseLawSearch":
        return f'CaseLawSearch("{text}")'

    if tool == "StatuteLookup":
        return f'StatuteLookup("16", "278")'  # placeholder (improve later)

    if tool == "LawLookup":
        return f'LawLookup("104", "104")'

    if tool == "DateCalculator":
        return f'DateCalculator("2021-01-01", "2021-02-01")'

    return None


# --- Execute tool ---
def run_tool(tool, text):
    try:
        if tool == "CaseLawSearch":
            return courtlistener_search(text)

        if tool == "StatuteLookup":
            return statute_lookup("16", "278")

        if tool == "LawLookup":
            return law_lookup("104", "104")

        if tool == "DateCalculator":
            return date_calculator("2021-01-01", "2021-02-01")

    except:
        return {"output": "API error"}

    return {"output": "No result"}



# --- Main function ---
def generate_candidates(texts):
    augmented_data = []

    for text in texts:
        tool = detect_tool(text)

        if not tool:
            continue

        tool_call = build_tool_call(tool, text)
        tool_result = run_tool(tool, text)

        output = tool_result.get("output", "")

        # 🔥 FILTER BAD OUTPUT
        if any(x in output for x in ["No results", "error", "not found"]):
            continue

        augmented_sample = {
            "original_text": text,
            "tool": tool,
            "tool_call": tool_call,
            "tool_output": output
        }

        augmented_data.append(augmented_sample)

    return augmented_data