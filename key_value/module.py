import numpy as np
import pandas as pd
import spacy
from spacy.pipeline import EntityRuler

from datasets import Dataset, Features, Value
from transformers import AutoTokenizer, AutoModel, TrainingArguments, Trainer
import evaluate



# Adjust Accordingly
CSV_PATH = "gemini_question_cypher_bio.csv"
TRAIN_TEST_SIZE = 0.1
TOKENIZER_NAME = "google-bert/bert-base-uncased"

# Load the Spacy Large Model
nlp = spacy.load('en_core_web_lg')

# Function to Annotate the Questions with BIO Tags
def annotate_bio_tags(df):
    df["bio_tags"] = ""

    for index, row in df.iterrows():
        text = row["question"]
        doc = nlp(text)

        final = []
        for e in doc:
            final.append(e.ent_iob_)

        df.loc[index, "bio_tags"] = " ".join(final)
        
def prepare_dataset(df):
    from datasets import Dataset, Features, Value

    # Define the features of your dataset.  This is crucial.
    features = Features({
        'text': Value('string'),
        'label': Value('string') 
    })

    # Preprocess the CSV
    df = df.rename(columns={'question': 'text', 'bio_tags': 'label'})
    df = df[["text", "label"]]
    
    # Map the BIO Tags into Integers
    bio_tag_map = {'O': 0, 'B': 1, 'I': 2}
    df['label'] = df['label'].apply(lambda x: [bio_tag_map[tag] for tag in x.split()])
    
    # Covnert into HuggingFace Dataset
    ds = Dataset.from_pandas(df)

    # Train Test Split
    ds = ds.train_test_split(test_size=TRAIN_TEST_SIZE)

    
def finetune_model(ds):

    # Load Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME)

    # Function to Tokenize Text
    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True)

    tokenized_datasets = ds.map(tokenize_function, batched=True)

    model = AutoModel.from_pretrained(TOKENIZER_NAME, num_labels=3, torch_dtype="auto")

    training_args = TrainingArguments(output_dir="test_trainer")

    metric = evaluate.load("accuracy")

    # Function to Evaluate Model's Accuracy
    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        return metric.compute(predictions=predictions, references=labels)

    # Configure Training Hyperparameters
    training_args = TrainingArguments(output_dir="test_trainer", eval_strategy="epoch")

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds["train"],
        eval_dataset=ds["test"],
        compute_metrics=compute_metrics,
    )

    trainer.train()

# Main Function
def main():
    """
    Main function for key value extraction module.
    
    """
    print("---------- Step 1: Annotate BIO Tags ---------- ")
    
    # Read the Filtered CSV File
    df = pd.read_csv("gemini_question_cypher_filtered.csv")
    
    # Annotate Questions with BIO Tags
    annotate_bio_tags(df)
    
    # Save the CSV
    df.to_csv(CSV_PATH, index=False)
    
    print("---------- Step 2: Prepare Fine-Tuning Dataset ---------- ")
    
    # Preprocess Dataset
    prepare_dataset(df)
    
    print("---------- Step 3: Fine-Tune Model ---------- ")
    
    # Preprocess Dataset
    finetune_model(ds)
        
if __name__ == "__main__":
    main()