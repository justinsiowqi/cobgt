from utils import read_question_cypher, write_cypher
from build_v1_nodes import remove_stopwords, chunk_and_tag    
from build_v2_nodes import run_cypher_lint, extract_parse_tree, build_hierarchy, split_parsed_trees, split_hierarchical_trees, find_label_type, extract_label_details, substitute_property_details, extract_match, extract_node_relationship
from connect_v1_v2_nodes import construct_graph, custom_plot
from connect_v1_v1_nodes import calculate_similarity, extract_similar_words, connect_graphs, complex_plot

from construct_graph import build_v1_nodes

sample_question = "Which films were helmed by Ron Howard that premiered before 1987?"

def main():
    """
    Main function for relation properties module.
    
    """
    word_terms = build_v1_nodes(sample_question)
    
    for term in word_terms:
        print(term)
    
if __name__ == "__main__":
    main()