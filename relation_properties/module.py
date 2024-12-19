from utils import read_question_cypher
from build_v1_nodes import remove_stopwords, chunk_and_tag    

def main():
    """
    Main function for relation properties module.
    
    """
    # Read the Question Cypher File
    qn1, cy1, qn2, cy2 = read_question_cypher("question_cypher.txt")

    # Remove Stopwords for Both Questions
    qn1_fil = remove_stopwords(qn1)
    qn2_fil = remove_stopwords(qn2)

    print(f"Removed Stopwords for Question 1: {qn1_fil}")
    print(f"Removed Stopwords for Question 2: {qn2_fil}")

    # Chunk and POS Tag Both Questions
    word_term1 = chunk_and_tag(qn1_fil)
    word_term2 = chunk_and_tag(qn2_fil)

    print(f"Word Term for Question 1: {word_term1}")
    print(f"Word Term for Question 2: {word_term2}")
    
if __name__ == "__main__":
    main()