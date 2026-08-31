# LearnPath Qwen training

This is an adapter-training pipeline, not a claim that the base model has been retrained in this repository. It creates a small synthetic domain set, optionally adds operator-approved Hugging Face exports, and trains a QLoRA adapter.

```bash
python training/prepare_dataset.py --output artifacts/learnpath.jsonl
python training/train_qwen_lora.py --data artifacts/learnpath.jsonl --output artifacts/qwen-learnpath-lora
```

Only add external datasets after reviewing their license, provenance, privacy, and task fit. Keep the resulting manifest with the model artifact. Evaluate on a held-out set and against the project’s structured-output tests before promoting an adapter.
