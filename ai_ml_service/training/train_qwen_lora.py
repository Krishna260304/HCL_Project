"""QLoRA/SFT entrypoint for the LearnPath-specific Qwen adapter."""

from __future__ import annotations

import argparse
from pathlib import Path

from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig
from trl import SFTTrainer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("artifacts/qwen-learnpath-lora"))
    parser.add_argument("--epochs", type=float, default=2.0)
    parser.add_argument("--max-seq-length", type=int, default=2048)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    dataset = load_dataset("json", data_files=str(args.data), split="train").train_test_split(test_size=0.1, seed=args.seed)
    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
    quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype="float16", bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, quantization_config=quant, device_map="auto", trust_remote_code=True)
    lora = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, bias="none", task_type="CAUSAL_LM", target_modules=["q_proj", "k_proj", "v_proj", "o_proj"])
    training = TrainingArguments(
        output_dir=str(args.output), num_train_epochs=args.epochs, learning_rate=2e-4,
        per_device_train_batch_size=1, gradient_accumulation_steps=16, gradient_checkpointing=True,
        logging_steps=10, save_strategy="epoch", evaluation_strategy="epoch", report_to="none",
        fp16=True, seed=args.seed,
    )
    trainer = SFTTrainer(model=model, tokenizer=tokenizer, train_dataset=dataset["train"], eval_dataset=dataset["test"],
                         dataset_text_field=None, max_seq_length=args.max_seq_length, packing=False,
                         args=training, peft_config=lora)
    trainer.train()
    trainer.save_model(str(args.output))
    tokenizer.save_pretrained(str(args.output))
    print(f"saved LearnPath adapter to {args.output}")


if __name__ == "__main__":
    main()
