from utils import read_question_cypher, write_cypher
from build_v1_nodes import remove_stopwords, chunk_and_tag    
from build_v2_nodes import run_cypher_lint, extract_parse_tree, build_hierarchy, split_parsed_trees, split_hierarchical_trees

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
    print("Removing the stopwords...")
    qn1_fil = remove_stopwords(qn1)
    qn2_fil = remove_stopwords(qn2)
    print(f"Question 1: {qn1_fil}")
    print(f"Question 2: {qn2_fil}")

    # Chunk and POS Tag Both Questions
    print("Obtaining the word terms...")
    word_term1 = chunk_and_tag(qn1_fil)
    word_term2 = chunk_and_tag(qn2_fil)
    print(f"Question 1: {word_term1}")
    print(f"Question 2: {word_term2}")
    
    print("---------- Step 2: Build V2 Nodes ---------- ")
    
    # Write a Cypher File Based on the Question Cypher File
    write_cypher(cy1, cy2, cyp_file_path)
          
    # Run Cypher Linter
    output = run_cypher_lint(cyp_file_path)
    
    # Extract and parse the parse tree
    parse_tree = extract_parse_tree(output)
    hierarchical_tree = build_hierarchy(parse_tree)
    
    # Split into Two Parsed Trees
    parse_tree1, parse_tree2 = split_parsed_trees(parse_tree)
    
    # Split into Two Hierarchical Trees
    hierarchical_tree1, hierarchical_tree2 = split_hierarchical_trees(hierarchical_tree)
    print(hierarchical_tree1)
    
if __name__ == "__main__":
    main()