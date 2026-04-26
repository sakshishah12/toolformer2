LEGAL_DEMOS = [

# --- CaseLawSearch ---
{
"question": "What case established school desegregation?",
"tool_call": 'CaseLawSearch("Brown v. Board of Education")',
"tool_output": "Brown v. Board of Education (Supreme Court)",
"final_answer": "Brown v. Board of Education established school desegregation."
},

{
"question": "Which case defined Miranda rights?",
"tool_call": 'CaseLawSearch("Miranda v. Arizona")',
"tool_output": "Miranda v. Arizona (Supreme Court)",
"final_answer": "Miranda v. Arizona defined Miranda rights."
},

# --- StatuteLookup ---
{
"question": "What does 16 U.S.C. § 278 cover?",
"tool_call": 'StatuteLookup("16", "278")',
"tool_output": "Public lands regulation | https://...",
"final_answer": "16 U.S.C. § 278 relates to public land regulation."
},

# --- LawLookup ---
{
"question": "What is Public Law 104-104?",
"tool_call": 'LawLookup("104", "104")',
"tool_output": "Telecommunications Act | Latest action: ...",
"final_answer": "Public Law 104-104 is the Telecommunications Act."
},

# --- DateCalculator ---
{
"question": "How many days between 2021-01-01 and 2021-02-01?",
"tool_call": 'DateCalculator("2021-01-01", "2021-02-01")',
"tool_output": "31 days",
"final_answer": "There are 31 days between the dates."
}

]