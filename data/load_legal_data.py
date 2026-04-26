from datasets import load_dataset

def load_legal_texts(limit=5000):
    """
    Loads legal texts from lex_glue (case_hold)
    Returns a list of strings (contexts)
    """

    print("Loading dataset...")

    dataset = load_dataset("lex_glue", "case_hold", split="train")

    print("Dataset loaded. Total samples:", len(dataset))

    texts = []

    for i in range(min(limit, len(dataset))):
        context = dataset[i]["context"]

        # Clean text (important)
        if context and isinstance(context, str):
            context = context.strip()

            # Optional: skip very short texts
            if len(context) > 50:
                texts.append(context)

    print("Collected texts:", len(texts))

    return texts


if __name__ == "__main__":
    texts = load_legal_texts(limit=5000)

    # Preview
    print("\n--- SAMPLE TEXT ---\n")
    print(texts[0][:500])  # first 500 chars

    # Save to file (optional but recommended)
    with open("raw/legal_texts.txt", "w", encoding="utf-8") as f:
        for t in texts:
            f.write(t.replace("\n", " ") + "\n")

    print("\nSaved to data/raw/legal_texts.txt")