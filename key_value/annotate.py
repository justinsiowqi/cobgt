import spacy

# Load the Spacy Large Model
nlp = spacy.load('en_core_web_lg')

# Function to Annotate the Questions with BIO Tags
def annotate_bio_tags(text):

    doc = nlp(text)
        
    final = []

    # Add O Tag for CLS Token
    final.append("O")

    for e in doc:
        final.append(e.ent_iob_)

    # Add O Tag for SEP Token
    final.append("O")

    return final