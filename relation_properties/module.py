from utils import read_question_cypher, write_cypher
from build_v1_nodes import remove_stopwords, chunk_and_tag    
from build_v2_nodes import run_cypher_lint, extract_parse_tree, build_hierarchy, split_parsed_trees, split_hierarchical_trees, find_label_type, extract_label_details, substitute_property_details, extract_match, extract_node_relationship
from connect_v1_v2_nodes import construct_graph, custom_plot
from connect_v1_v1_nodes import calculate_similarity, extract_similar_words

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
    # print(hierarchical_tree1)
    
    # Extract Properties
    tree1_prop = find_label_type(hierarchical_tree1, "property")
    tree2_prop = find_label_type(hierarchical_tree2, "property")

    # Extract Identifiers
    tree1_identifier = find_label_type(hierarchical_tree1, "identifier")
    tree2_identifier = find_label_type(hierarchical_tree2, "identifier")

    # Extract Property Names
    tree1_prop_name = find_label_type(hierarchical_tree1, "prop name")
    tree2_prop_name = find_label_type(hierarchical_tree2, "prop name")
    
    # Extract Property Details
    tree1_prop_details = extract_label_details(tree1_prop)
    tree2_prop_details = extract_label_details(tree2_prop)

    # Convert the Identifiers List and Property Names List into a Dictionary
    tree1_identifier_dict = {item['id']: item['details'].replace("`", "") for item in tree1_identifier}
    tree1_prop_name_dict = {item['id']: item['details'].replace("`", "") for item in tree1_prop_name}
    tree2_identifier_dict = {item['id']: item['details'].replace("`", "") for item in tree2_identifier}
    tree2_prop_name_dict = {item['id']: item['details'].replace("`", "") for item in tree2_prop_name}
    
    # Extract the Properties from Both Trees
    tree1_prop_list = substitute_property_details(tree1_prop_details, tree1_identifier_dict, tree1_prop_name_dict)
    tree2_prop_list = substitute_property_details(tree2_prop_details, tree2_identifier_dict, tree2_prop_name_dict)
    
    # Extract the MATCH id for Both Trees
    tree1_match_id = extract_match(parse_tree1)
    tree2_match_id = extract_match(parse_tree2)
    
    # Extact the Relationships from Both Trees
    tree1_rel_list = extract_node_relationship(parse_tree1, tree1_match_id)
    tree2_rel_list = extract_node_relationship(parse_tree2, tree2_match_id)

    # Combine the Relationship and Properties into a Single List
    tree1_rel_prop = tree1_rel_list + tree1_prop_list
    tree2_rel_prop = tree2_rel_list + tree2_prop_list

    print(f"Tree 1 Relationship and Properties: {tree1_rel_prop}")
    print(f"Tree 2 Relationship and Properties: {tree2_rel_prop}")
    
    print("---------- Step 3: Connect V1 and V2 Nodes ---------- ")
    
    # Reverse the List so the Plot Shows Rightside Up
    word_term1_rev = word_term1[::-1]
    rel_prop1_rev = tree1_rel_prop[::-1]

    word_term2_rev = word_term2[::-1]
    rel_prop2_rev = tree2_rel_prop[::-1]
    
    # Construct the Graphs for Both Questions and Cypher Statements
    G1 = construct_graph(word_term1_rev, rel_prop1_rev)
    G2 = construct_graph(word_term2_rev, rel_prop2_rev)
    
    # Plot Graph 1
    custom_plot(G1, word_term1_rev, rel_prop1_rev, "graph1.png")

    # Plot Graph 2
    custom_plot(G2, word_term2_rev, rel_prop2_rev, "graph2.png")
    
    print("Graph 1 and Graph 2 saved successfully.")
    
    print("---------- Step 4: Connect V1 and V1 Nodes ---------- ")
    
    # Extract the Word Terms Without Their POS Tags
    word_term1_notag = chunk_and_tag(qn1_fil, return_tag=False)
    word_term2_notag = chunk_and_tag(qn2_fil, return_tag=False)
    
    print(f"Word Term (No Tag) for Question 1: {word_term1_notag}")
    print(f"Word Term (No Tag) for Question 2: {word_term2_notag}")
    
    # Encode and Calculate Similarity Scores
    sim_scores = calculate_similarity(word_term1_notag, word_term2_notag)
    
    # Extract Similar Word Terms Above 0.65 Threshold
    sim_words = extract_similar_words(sim_scores)
    print(f"Text Similarity Score > 0.65: {sim_words}")
    
if __name__ == "__main__":
    main()