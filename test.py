from pipeline.legal_demo import generate_candidates

texts = [
    "The case Brown v. Board of Education changed constitutional law.",
    "According to 16 U.S.C. 278, environmental protections apply.",
    "Public Law 104-104 changed telecom regulations.",
    "The time between 2021-01-01 and 2021-02-01 is important."
]

data = generate_candidates(texts)

for d in data:
    print("\n---")
    print(d)