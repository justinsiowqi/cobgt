from build_nodes import build_v1_nodes, build_v2_nodes
from connect_nodes import connect_v1_v1_nodes, connect_v1_v2_nodes
from construct_graph import fetch_all_word_terms

sample_question = "Which films were helmed by Ron Howard that premiered before 1987?"

def main():
    """
    Main function for relation properties module.
    
    """
    # Chunk Question and Perform POS-Tagging
    word_terms = build_v1_nodes(sample_question)
    
    for word_term in word_terms:
                
        all_word_terms = fetch_all_word_terms()
        print(all_word_terms)
        
        # Check if Token Exists in the Train Data
        if word_term not in all_word_terms:
            print(f"Token {word_term} does not exist in train data! Performing similarity search...")
        else:
            print(f"Token {word_term} exists in train data!")
    
if __name__ == "__main__":
    main()