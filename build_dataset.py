import json
from pipeline.generate_candidates import generate_candidates
from pipeline.filter_by_loss import filter_by_loss


# -----------------------------
# LOAD RAW TEXT
# -----------------------------
def load_raw_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        texts = [line.strip() for line in f if len(line.strip()) > 50]
    return texts


# -----------------------------
# BUILD DATASET PIPELINE
# -----------------------------
def build_dataset(input_path, output_path, limit=5000):

    print("Loading raw text...")
    texts = load_raw_text(input_path)

    # limit size (for speed)
    texts = texts[:limit]

    print(f"Raw texts: {len(texts)}")

    # -------------------------
    # STEP 1: Generate candidates
    # -------------------------
    print("\nGenerating candidates...")
    candidates = generate_candidates(texts)

    print(f"Candidates generated: {len(candidates)}")

    # -------------------------
    # STEP 2: Loss filtering
    # -------------------------
    print("\nFiltering using loss...")
    filtered = filter_by_loss(candidates)

    print(f"Filtered samples: {len(filtered)}")

    # -------------------------
    # STEP 3: Format for training
    # -------------------------
    train_data = [{"text": d["augmented_text"]} for d in filtered]

    # -------------------------
    # SAVE
    # -------------------------
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(train_data, f, indent=2)

    print("\nDataset saved to:", output_path)
    print("Final dataset size:", len(train_data))


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    build_dataset(
        input_path="data/raw/legal_texts.txt",
        output_path="data/processed/train.json",
        limit=5000
    )