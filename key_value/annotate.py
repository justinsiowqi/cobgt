import spacy

# Load the Spacy Large Model
nlp = spacy.load('en_core_web_lg')

def annotate_bio_tags(text):
    """
    Annotate each word in the sentence with BIO tags.
    
    Args:
        text: The sentence you want to annotate.
        
    Returns:
        final: The annotated sentence.
    """
    doc = nlp(text)
        
    final = []

    # Add O Tag for CLS Token
    final.append("O")

    for e in doc:
        final.append(e.ent_iob_)

    # Add O Tag for SEP Token
    final.append("O")

    return final