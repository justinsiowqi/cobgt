from utils import read_question_cypher, write_cypher
from build_v1_nodes import remove_stopwords, chunk_and_tag    
from build_v2_nodes import run_cypher_lint, extract_parse_tree, build_hierarchy

# Define File Paths Here
cyp_file_path = "cypher.cyp"

def main():
    """
    Main function for relation properties module.
    
    """
    print("---------- Step 1: Build V1 Nodes ---------- ")
    
    # Read the Question Cypher File
    qn1, cy1, qn2, cy2 = read_question_cypher("question_cypher.txt")

    # Remove Stopwords for Both Questions
    print("Removing the stopwords..."
    qn1_fil = remove_stopwords(qn1)
    qn2_fil = remove_stopwords(qn2)
    print(f"Question 1: {qn1_fil}")
    print(f"Question 2: {qn2_fil}")

    # Chunk and POS Tag Both Questions
    print("Obtaining the word terms..."
    word_term1 = chunk_and_tag(qn1_fil)
    word_term2 = chunk_and_tag(qn2_fil)
    print(f"Question 1: {word_term1}")
    print(f"Question 2: {word_term2}")
    
    print("---------- Step 2: Build V2 Nodes ---------- ")
    
    # Write a Cypher File Based on the Question Cypher File
    write_cypher(cy1, cy2, cyp_file_path)
          
    # Run Cypher Linter
    output = run_cypher_lint(cyp_file_path)
    
if __name__ == "__main__":
    main()