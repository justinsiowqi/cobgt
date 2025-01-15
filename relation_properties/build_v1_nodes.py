import nltk
from nltk.corpus import stopwords
from nltk import pos_tag, word_tokenize
from nltk.chunk import ne_chunk

# ---------- Step 1: Remove Stopwords ----------

# Download the necessary NLTK data files
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('maxent_ne_chunker_tab')
nltk.download('maxent_ne_chunker')
nltk.download('words')

# Get a List of Stopwords from NLTK
stop_list = stopwords.words("english")

# Function to Remove Stopwords from Question
def remove_stopwords(qn):
    """
    Remove the stopwords from a sentence.
    
    Args:
        qn: The natural language question.
    
    Returns:
        qn_fil: The filtered natural language question with stopwords removed.
    """
    qn_list = qn.split(" ")

    qn_list_fil = []
    for word in qn_list:
        if word not in stop_list:
            qn_list_fil.append(word)

    qn_fil = " ".join(qn_list_fil)
    return qn_fil


# ---------- Step 2: POS Tagging and Chunking ----------

# Function to Chunk and POS Tag Sentences
def chunk_and_tag(qn_fil, return_tag=True):
    """
    Chunk and POS-Tag a sentence.
    
    Args:
        qn_fil: The filtered natural language question with stopwords removed.
        return_tag: By default, the POS tags are returned.
    
    Returns:
        word_term: A list of words from the filtered question. Each word comes with a POS-Tag.
    """
    # Perform Chunking
    tokens = word_tokenize(qn_fil)
    chunked_output = []
    for token in tokens:
        chunked_output.append(token)

    # Clean the Chunked Output by Keeping Only Alphanumeric
    filtered_output = [word for word in chunked_output if word.isalnum()]

    # Perform POS Tagging
    pos_tags = pos_tag(filtered_output)
    
    # Convert POS Tags from Set to String
    if return_tag:
        word_term = [label + f" {tag}" for label, tag in pos_tags]
    else:
        word_term = [label for label, tag in pos_tags]
        
    return word_term
