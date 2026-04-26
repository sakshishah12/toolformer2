from datasets import load_dataset
import os


# -----------------------------
# DATASET OPTIONS (tried in order)
# -----------------------------
DATASET_OPTIONS = [
    # Tier 1: Best — 6.7M real U.S. court opinions, public domain, no auth
    {
        "path": "free-law/Caselaw_Access_Project",
        "name": None,
        "text_field": "text",
        "label": "free-law/Caselaw_Access_Project",
    },
    # Tier 2: LegalBench — statutes, contracts, judicial opinions, no auth
    {
        "path": "nguha/legalbench",
        "name": "learned_hands_courts",   # judicial opinion subset
        "text_field": "text",
        "label": "nguha/legalbench (learned_hands_courts)",
    },
    # Tier 3: lex_glue but with the 'ecthr_a' subset — ECtHR court decisions,
    #         much cleaner than case_hold for sentence-level text
    {
        "path": "lex_glue",
        "name": "ecthr_a",
        "text_field": "text",
        "label": "lex_glue/ecthr_a",
    },
]


def load_legal_texts(limit=1000):
    dataset = None
    text_field = "text"

    for option in DATASET_OPTIONS:
        try:
            print(f"Trying: {option['label']} ...")
            kwargs = dict(split="train", streaming=True, trust_remote_code=True)
            if option["name"]:
                kwargs["name"] = option["name"]

            dataset = load_dataset(option["path"], **kwargs)
            text_field = option["text_field"]
            print(f"✓ Loaded: {option['label']}")
            break

        except Exception as e:
            print(f"  ✗ Failed: {e}")
            continue

    if dataset is None:
        raise RuntimeError(
            "All dataset options failed. "
            "Run: huggingface-cli login   (get token from huggingface.co/settings/tokens)"
        )

    # -------------------------
    # EXTRACT SENTENCES
    # -------------------------
    texts = []

    for sample in dataset:
        if len(texts) >= limit:
            break

        raw = sample.get(text_field, "")

        # ecthr_a returns a list of strings per sample
        if isinstance(raw, list):
            raw = " ".join(raw)

        if not isinstance(raw, str) or len(raw.strip()) < 50:
            continue

        for sentence in raw.split(". "):
            sentence = sentence.strip()
            if len(sentence) > 50:
                texts.append(sentence)
            if len(texts) >= limit:
                break

    print(f"Collected texts: {len(texts)}")
    return texts


if __name__ == "__main__":
    texts = load_legal_texts(limit=1000)

    if texts:
        print("\n--- SAMPLE TEXT ---\n")
        print(texts[0][:300])

    os.makedirs("data/raw", exist_ok=True)

    with open("data/raw/legal_texts.txt", "w", encoding="utf-8") as f:
        for t in texts:
            f.write(t.replace("\n", " ") + "\n")

    print("\nSaved to data/raw/legal_texts.txt")