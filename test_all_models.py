import os
import json
import warnings
from pathlib import Path

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

try:
    import torch
    import torch.nn.functional as F
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
except ImportError:
    print(
        "Error: Required libraries not found. Run this inside the backend/.venv environment."
    )
    exit(1)

# List of specific sentences to test
# Includes a mix of literal and sarcastic phrasing in Algerian Arabic / Standard Arabic
test_sentences = [
    # Sarcastic / Ironic
    "واش هاد القفازة، حرقت الماكلة ورايح تضحك",
    "يعطيك الصحة خويا، كملت الخدمة في عامين برك، ماشاء الله على السرعة!",
    "طبعاً الإنترنت عندنا أسرع من الضوء، تحمل صورة في يومين.",
    # Literal / Normal
    "شكرا على المساعدة، العمل كان ممتاز جدا وعجبني.",
    "اليوم الجو شباب بزاف، مليح تخرج تحوس فيه.",
    "وصلتني الطلبية في الوقت المحدد، خدمة ممتازة.",
]


def _is_hf_checkpoint(path: Path) -> bool:
    return (path / "config.json").exists() and (
        (path / "model.safetensors").exists() or (path / "pytorch_model.bin").exists()
    )


def find_all_models(root_dir: Path):
    print(f"Scanning for models in {root_dir}...")
    model_paths = []
    # Just look through immediate subdirectories to avoid deep node_modules or .venv matching
    for p in root_dir.glob("**/config.json"):
        if ".venv" in p.parts or "node_modules" in p.parts:
            continue
        model_dir = p.parent
        if _is_hf_checkpoint(model_dir) and model_dir not in model_paths:
            model_paths.append(model_dir)
    return model_paths


def test_models():
    project_root = Path(__file__).resolve().parent
    model_dirs = find_all_models(project_root)

    print(f"\nFound {len(model_dirs)} model architectures:")
    for m in model_dirs:
        print(f" - {m.relative_to(project_root)}")

    for model_path in model_dirs:
        print(f"\n{'='*70}")
        print(f"Testing Model: {model_path.relative_to(project_root)}")
        print(f"{'='*70}")

        try:
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForSequenceClassification.from_pretrained(model_path)
            model.eval()

            # Force threshold to 0.4 parameter
            threshold = 0.4

            print(f"Using threshold: {threshold}")
            print("-" * 70)

            for text in test_sentences:
                # Tokenize and predict
                encoded = tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=128,
                    padding=True,
                )

                with torch.no_grad():
                    logits = model(**encoded).logits
                    probabilities = F.softmax(logits, dim=-1)[0]

                # Assuming class 1 is Sarcastic
                prob_sarcastic = float(probabilities[1].item())
                is_sarcastic = prob_sarcastic >= threshold

                label = "SARCASTIC" if is_sarcastic else "LITERAL  "
                print(f"Text : {text}")
                print(
                    f"Pred : [{label}] | Sarcasm Prob: {prob_sarcastic:.4f} | Conf: {max(float(probabilities[0].item()), prob_sarcastic):.4f}"
                )
                print("-" * 70)

        except Exception as e:
            print(
                f"-> Failed to run inference on {model_path.relative_to(project_root)}: {e}"
            )


if __name__ == "__main__":
    test_models()
