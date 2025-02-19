import pandas as pd
from transformers import BertTokenizer, BertForTokenClassification

from annotate import annotate_bio_tags
from model import finetune_model, predict_bio_tags

# Adjust Accordingly
INPUT_CSV = "../data/processed/gemini_question_cypher_filtered.csv"
OUTPUT_CSV = "../data/processed/gemini_question_cypher_bio.csv"

TRAIN_TEST_SIZE = 0.1
MODEL_NAME = "google-bert/bert-base-cased"
MAX_LENGTH = 128

sample_question = "Which movies include Helen Hunt as part of the cast?"

# Main Function
def main():
    """
    Main function for key value extraction module.
    
    """
    print("---------- Step 1: Annotate BIO Tags ---------- ")
    
    # Read the Filtered CSV File
    df = pd.read_csv(INPUT_CSV)
    
    # Annotate Questions with BIO Tags
    df["bio_tags"] = ""

    for index, row in df.iterrows():
        final = annotate_bio_tags(row["question"])
        df.loc[index, "bio_tags"] = " ".join(final)
    
    # Save the CSV
    df.to_csv(OUTPUT_CSV, index=False)
    
    print("---------- Step 2: Fine-Tune Model ---------- ")
    
    # Convert Question and BIO Tags to List
    questions = df['question'].tolist()
    bio_tags = df['bio_tags'].tolist()
    
    # Finetune the Model
    model, tokenizer = finetune_model(MODEL_NAME, questions, bio_tags)

    print("---------- Step 3: Run Inference ---------- ")
    
    # Load Fine-Tuned Model and Tokenizer
    tokenizer = BertTokenizer.from_pretrained("bert-base-cased")
    model = BertForTokenClassification.from_pretrained("results/checkpoint-210", num_labels=3)
    
    # Run Inference
    print(sample_question)
    predicted_tags = predict_bio_tags(sample_question, model, tokenizer)
    print(predicted_tags)
    
    # Map BIO Tags to Natural Language Question
    tokens = tokenizer.tokenize(sample_question)
    
    # Check if Tokens and BIO Tags Match
    if len(tokens) == len(predicted_tags):
    
        final = []
        for idx, item in enumerate(predicted_tags):
            if item != "O":
                final.append(tokens[idx])
        print(f"Key value sucessfully extracted: {final}")
    
    else:
        print("Error: Tokens and BIO tags do not match.")
        
if __name__ == "__main__":
    main()