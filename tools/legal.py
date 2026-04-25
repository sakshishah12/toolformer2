import requests
from datetime import datetime
import time

import requests
from requests.exceptions import RequestException
import time

def courtlistener_search(query, max_results=3):
    url = "https://www.courtlistener.com/api/rest/v4/search/"

    headers = {
        "Authorization": "e0d212a7b11115fac5a7b993998e78324f028c48",
        "Accept": "application/json"
    }

    params = {
        "q": query,
        "type": "o",
    }

    summaries = []

    for attempt in range(3):
        try:
            res = requests.get(url, params=params, headers=headers, timeout=10)

            if res.status_code == 200:
                data = res.json()
                results = data.get("results", [])[:max_results]

                for r in results:
                    case_name = r.get("caseName", "Unknown case")
                    court = r.get("court_citation_string", r.get("court", "Unknown court"))
                    summaries.append(f"{case_name} ({court})")
                break
            elif res.status_code == 429:
                time.sleep(2 ** attempt)  # exponential backoff
            else:
                summaries = [f"API error: HTTP {res.status_code}"]
                break

        except RequestException as e:
            if attempt == 2:
                summaries = [f"Network error: {e}"]
            time.sleep(2)

    if not summaries:
        summaries = ["No results found"]

    return {
        "tool": "CourtListenerSearch",
        "input": query,
        "output": "; ".join(summaries)
    }

import requests
import os

import requests
import os

def statute_lookup(usc_title, section):
    """
    usc_title: USC title number, e.g. "16"
    section:   section number,   e.g. "278"
    """
    api_key = os.environ["GOVINFO_API_KEY"]
    search_url = f"https://api.govinfo.gov/search?api_key={api_key}"

    # Correct citation query format per govinfo docs
    payload = {
        "query": f'collection:uscode citation:"{usc_title} U.S.C. {section}"',
        "pageSize": "1",           # must be a STRING, not int
        "offsetMark": "*",
        "resultLevel": "default"   # returns granule-level results
    }

    try:
        res = requests.post(
            search_url,
            json=payload,
            timeout=10
        )
        res.raise_for_status()
        data = res.json()

        results = data.get("results", [])
        if not results:
            return {
                "tool": "StatuteLookup",
                "input": f"{usc_title} U.S.C. § {section}",
                "output": "Statute not found"
            }

        item = results[0]
        title_text = item.get("title", "No title available")
        package_id = item.get("packageId", "")
        granule_id = item.get("granuleId", "")

        if granule_id:
            source = f"https://www.govinfo.gov/app/details/{package_id}/{granule_id}"
        elif package_id:
            source = f"https://www.govinfo.gov/app/details/{package_id}"
        else:
            source = "No link available"

        output = f"{title_text} | {source}"

    except requests.exceptions.HTTPError as e:
        output = f"HTTP error: {e}"
    except requests.exceptions.RequestException as e:
        output = f"Network error: {e}"

    return {
        "tool": "StatuteLookup",
        "input": f"{usc_title} U.S.C. § {section}",
        "output": output
    }

# --- Congress.gov API: Bill summary by public law number ---
def law_lookup(congress, law_number):
    """
    Look up a public law and get its CRS summary.
    congress: e.g. "104"
    law_number: e.g. "104" (for Public Law 104-104)
    """
    api_key = os.environ["CONGRESS_API_KEY"]
    url = f"https://api.congress.gov/v3/law/{congress}/pub/{law_number}"
    params = {
        "api_key": api_key,
        "format": "json"
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()

        bill = data.get("bill", {})
        title = bill.get("title", "No title")
        latest_action = bill.get("latestAction", {}).get("text", "No action info")

        output = f"{title} | Latest action: {latest_action}"

    except requests.exceptions.RequestException as e:
        output = f"Network error: {e}"

    return {
        "tool": "LawLookup",
        "input": f"Public Law {congress}-{law_number}",
        "output": output
    }


# --- Date Calculator ---
def date_calculator(from_date, to_date):
    fmt = "%Y-%m-%d"

    try:
        d1 = datetime.strptime(from_date, fmt)
        d2 = datetime.strptime(to_date, fmt)
        delta = (d2 - d1).days
        result = f"{delta} days"
    except:
        result = "Invalid date format"

    return {
        "tool": "DateCalculator",
        "input": f"{from_date} → {to_date}",
        "output": result
    }