import re
from tools.legal import (
    statute_lookup,
    law_lookup,
    date_calculator,
    courtlistener_search
)

# -----------------------------
# TOOL DETECTION
# -----------------------------
def detect_tool(text):
    t = text.lower()

    # Check statute before case law — avoids "18 U.S.C. § 924" being grabbed by " v." match
    if re.search(r"\d+\s*u\.s\.c\.?\s*[§s]?\s*\d+", t):
        return "StatuteLookup"

    if "public law" in t:
        return "LawLookup"

    # FIX: require capital letters on both sides of v. to reduce false positives
    if re.search(r'[A-Z][a-zA-Z .&,]+ v\. [A-Z][a-zA-Z]', text):
        return "CaseLawSearch"

    if re.search(r"\d{4}-\d{2}-\d{2}", text):
        return "DateCalculator"

    return None


# -----------------------------
# ARGUMENT EXTRACTION
# -----------------------------
def extract_case_name(text):
    # FIX: allow multi-word party names (e.g., "United States v. Newman")
    match = re.search(
        r'((?:[A-Z][a-zA-Z&.,]+(?: [A-Z][a-zA-Z&.,]+)*) v\. (?:[A-Z][a-zA-Z&.,]+(?: [A-Z][a-zA-Z&.,]+)*))',
        text
    )
    return match.group(1) if match else None


def extract_statute(text):
    # FIX: handle "18 U.S.C. § 924" — § and section number may be separated by spaces
    match = re.search(r"(\d+)\s*U\.S\.C\.?\s*[§Ss]?\s*(\d+)", text)
    return match.groups() if match else None


def extract_dates(text):
    matches = re.findall(r"\d{4}-\d{2}-\d{2}", text)
    return matches if len(matches) >= 2 else None


def extract_law(text):
    match = re.search(r"Public Law (\d+)-(\d+)", text)
    return match.groups() if match else None


# -----------------------------
# TOOL CALL BUILDER
# -----------------------------
def build_tool_call(tool, text):
    if tool == "CaseLawSearch":
        case = extract_case_name(text)
        if case:
            return f'CaseLawSearch("{case}")', case

    if tool == "StatuteLookup":
        statute = extract_statute(text)
        if statute:
            return f'StatuteLookup("{statute[0]}", "{statute[1]}")', statute

    if tool == "LawLookup":
        law = extract_law(text)
        if law:
            return f'LawLookup("{law[0]}", "{law[1]}")', law

    if tool == "DateCalculator":
        dates = extract_dates(text)
        if dates:
            return f'DateCalculator("{dates[0]}", "{dates[1]}")', dates

    return None, None


# -----------------------------
# TOOL EXECUTION
# -----------------------------
def run_tool(tool, args):
    try:
        if tool == "CaseLawSearch":
            return courtlistener_search(args)

        if tool == "StatuteLookup":
            return statute_lookup(args[0], args[1])

        if tool == "LawLookup":
            return law_lookup(args[0], args[1])

        if tool == "DateCalculator":
            return date_calculator(args[0], args[1])

    except Exception as e:
        return {"output": f"API error: {e}"}

    return {"output": "No result"}


# -----------------------------
# INSERT TOOL INTO TEXT
# -----------------------------
def insert_tool(text, tool_call, output):
    return f"{text} [{tool_call} → {output}]"


# -----------------------------
# MAIN PIPELINE  (add debug logging)
# -----------------------------
def generate_candidates(texts, debug=False):
    augmented_data = []

    for text in texts:
        tool = detect_tool(text)
        if not tool:
            if debug:
                print(f"[SKIP] No tool detected: {text[:80]!r}")
            continue

        tool_call, args = build_tool_call(tool, text)
        if not tool_call:
            if debug:
                print(f"[SKIP] Extraction failed for {tool}: {text[:80]!r}")
            continue

        tool_result = run_tool(tool, args)
        output = tool_result.get("output", "")

        if any(x in output.lower() for x in ["no results", "error", "not found"]):
            if debug:
                print(f"[SKIP] Bad output for {tool_call}: {output!r}")
            continue

        output = output.split(";")[0]
        augmented_text = insert_tool(text, tool_call, output)

        augmented_data.append({
            "original_text": text,
            "augmented_text": augmented_text,
            "tool": tool,
            "tool_call": tool_call,
            "tool_output": output
        })

    return augmented_data