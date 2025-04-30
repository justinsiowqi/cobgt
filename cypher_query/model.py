import os
import pandas as pd
import torch
from datasets import Dataset
from transformers import (
    T5ForConditionalGeneration, AutoTokenizer,
    DataCollatorForSeq2Seq, Trainer, TrainingArguments
)

def format_input(R, K, Q):
    D1 = "With this information: "
    D2 = "Key value: "
    D3 = "Convert to Cypher query: "

    input_text = (
        f"<CLS>{D1}{R} <SEP>{D2}{K} <SEP>{D3}{Q} <EOS>"
    )
    return input_text

def prepare_dataset(df):
    df["input_sequence"] = df.apply(
        lambda r: format_input(r["relation_properties"], r["key_values"], r["question"]),
        axis=1
    )
    df = df[["input_sequence", "cypher"]]
    ds = Dataset.from_dict(df.to_dict(orient="list"))
    ds = ds.train_test_split(test_size=0.2)
    
    return ds

def finetune_model(ds, tokenizer, model):
    
    # Define the Nested Tokenizing Function
    def tokenize_fn(ex):
        inp = tokenizer(ex["input_sequence"], truncation=True, padding="longest")
        with tokenizer.as_target_tokenizer():
            tgt = tokenizer(ex["cypher"], truncation=True)
        inp["labels"] = tgt["input_ids"]
        return inp
        
    # Tokenize the Questions
    dataset = ds.map(
        tokenize_fn,
        batched=True,
        remove_columns=["input_sequence", "cypher"],
    )
    
    # Instantiate Data Collator
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
    
    # Define Training Arguments
    training_args = TrainingArguments(
        output_dir="./results",
        evaluation_strategy="epoch",
        learning_rate=5e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=10,
    )

    # Initialize the Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset= dataset.get("validation", dataset["test"]),
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    trainer.train()
    
    # Save the Model
    trainer.save_model(training_args.output_dir)
    
    return model, tokenizer

def load_latest_checkpoint():
    ckpts = [
        os.path.join("results", d)
        for d in os.listdir("results")
        if d.startswith("checkpoint-")
    ]
    if not ckpts:
        raise RuntimeError("No checkpoints found in ./results")
    
    ckpts = sorted(ckpts, key=lambda x: int(x.split("-")[-1]))
    latest_ckpt = ckpts[-1]
    return latest_ckpt

def predict_cypher(input_text, tokenizer, model):
    # Tokenize the Input
    tokens = tokenizer(
        input_text,
        return_tensors="pt",
        truncation=True,
        padding=True,             
    )
    tokens = {k: v.to(model.device) for k, v in tokens.items()}

    # Generate
    with torch.no_grad():
        output_ids = model.generate(
            input_ids=tokens["input_ids"],
            attention_mask=tokens["attention_mask"],
            max_new_tokens=128,
            num_beams=4,
            early_stopping=True,        
            no_repeat_ngram_size=2,
        )

    # Decode
    return tokenizer.decode(output_ids[0], skip_special_tokens=True)