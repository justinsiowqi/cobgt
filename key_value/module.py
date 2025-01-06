import numpy as np
import pandas as pd
import spacy
from spacy.pipeline import EntityRuler

from datasets import Dataset, Features, Value
from transformers import AutoTokenizer, AutoModel, TrainingArguments, Trainer
import evaluate

from model import finetune_model, predict_bio_tags

# Adjust Accordingly
CSV_PATH = "gemini_question_cypher_bio.csv"
TRAIN_TEST_SIZE = 0.1
MODEL_NAME = "google-bert/bert-base-cased"
MAX_LENGTH = 128

sample_question = "Which movies include Helen Hunt as part of the cast?"

# Load the Spacy Large Model
nlp = spacy.load('en_core_web_lg')

# Function to Annotate the Questions with BIO Tags
def annotate_bio_tags(df):
    df["bio_tags"] = ""

    for index, row in df.iterrows():
        text = row["question"]
        doc = nlp(text)
        
        final = []

        # Add O Tag for CLS Token
        final.append("O")
        
        for e in doc:
            final.append(e.ent_iob_)
        
        # Add O Tag for SEP Token
        final.append("O")

        df.loc[index, "bio_tags"] = " ".join(final)

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

    df = pd.read_csv(CSV_PATH)
    
    print("---------- Step 2: Fine-Tune Model ---------- ")
    
    # Convert Question and BIO Tags to List
    questions = df['question'].tolist()
    bio_tags = df['bio_tags'].tolist()
    
    # Finetune the Model
    model, tokenizer = finetune_model(MODEL_NAME, questions, bio_tags)

    print("---------- Step 3: Test Model---------- ")
    
    # Test Model
    print(sample_question)
    predicted_tags = predict_bio_tags(sample_question, model, tokenizer)
    print(predicted_tags)
        
if __name__ == "__main__":
    main()