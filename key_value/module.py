import numpy as np
import pandas as pd
import spacy
from spacy.pipeline import EntityRuler

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
            final.append(e.text)
            final.append(e.ent_iob_)

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
    df.to_csv("gemini_question_cypher_bio.csv", index=False)
        
if __name__ == "__main__":
    main()