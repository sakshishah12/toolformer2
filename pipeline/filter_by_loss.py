import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm

MODEL_NAME = "distilgpt2"
BATCH_SIZE = 16          # tune up if you have a larger GPU (e.g. 32 for 16GB+)
MAX_LENGTH = 128

device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# distilgpt2 has no pad token — must set one before batching
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(MODEL_NAME).to(device)
model.eval()


# -----------------------------
# BATCHED LOSS FUNCTION
# -----------------------------
def compute_losses_batch(texts: list[str]) -> list[float]:
    """
    Compute per-sample cross-entropy loss for a batch of texts.
    Returns a list of floats, one per input text.
    """
    inputs = tokenizer(
        texts,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_LENGTH,
        padding=True,               # pad to longest in batch
        return_attention_mask=True,
    ).to(device)

    with torch.no_grad():
        outputs = model(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
        )
        logits = outputs.logits   # (B, T, V)

    losses = []
    for i in range(len(texts)):
        # Build labels: mask padding tokens with -100 so they're ignored
        labels = inputs["input_ids"][i].clone()
        pad_mask = inputs["attention_mask"][i] == 0
        labels[pad_mask] = -100

        # Shift for causal LM: predict token t+1 from token t
        shift_logits = logits[i, :-1, :]          # (T-1, V)
        shift_labels = labels[1:]                  # (T-1,)

        loss = torch.nn.functional.cross_entropy(
            shift_logits, shift_labels, ignore_index=-100
        )
        losses.append(loss.item())

    return losses


# -----------------------------
# FILTER FUNCTION
# -----------------------------
def filter_by_loss(samples: list[dict], debug: bool = False) -> list[dict]:
    filtered = []
    debug_count = 0

    # Process in batches
    for batch_start in tqdm(range(0, len(samples), BATCH_SIZE), desc="Filtering"):
        batch = samples[batch_start: batch_start + BATCH_SIZE]

        originals  = [s["original_text"]  for s in batch]
        augmented  = [s["augmented_text"] for s in batch]

        try:
            losses_orig = compute_losses_batch(originals)
            losses_aug  = compute_losses_batch(augmented)
        except Exception as e:
            print(f"[WARN] Batch failed: {e}")
            continue

        for i, sample in enumerate(batch):
            lo = losses_orig[i]
            la = losses_aug[i]

            if debug and debug_count < 5:
                print("\n--- SAMPLE DEBUG ---")
                print("Original :", sample["original_text"][:80])
                print("Augmented:", sample["augmented_text"][:80])
                print(f"Loss original: {lo:.4f}  |  Loss augmented: {la:.4f}")
                debug_count += 1

            if la < lo:
                filtered.append(sample)

    print(f"\nFiltered samples: {len(filtered)} / {len(samples)}")
    return filtered