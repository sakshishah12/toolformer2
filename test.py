from pipeline.generate_candidates import generate_candidates
from pipeline.filter_by_loss import filter_by_loss

texts = [
    "The case Brown v. Board of Education changed constitutional law.",
    "According to 16 U.S.C. § 278, environmental protections apply.",
    "The time between 2021-01-01 and 2021-02-01 is important."
]

candidates = generate_candidates(texts)
filtered = filter_by_loss(candidates)

print("\n=== FILTERED DATA ===\n")

for f in filtered:
    print(f["augmented_text"])
    print("Loss original:", f["loss_original"])
    print("Loss augmented:", f["loss_augmented"])
    print("-----")