import pandas as pd
from utils import read_question_cypher, write_cypher, append_cypher
from build_v1_nodes import remove_stopwords, chunk_and_tag 
from build_v2_nodes import run_cypher_lint, extract_parse_tree, build_hierarchy, split_parsed_trees, split_hierarchical_trees, find_label_type, extract_label_details, substitute_property_details, extract_match, extract_node_relationship

# Define File Paths Here
cyp_file_path = "cypher.cyp"
all_cyp_file_path = "all_cypher.cyp"

# Read the Question Schema Relationship CSV File
df = pd.read_csv("question_schema_relationship.csv")

def build_v1_nodes(question):
    
    # Remove Stopwords the Question
    qn_fil = remove_stopwords(question)
    
    # Chunk and POS Tag the Question
    word_term = chunk_and_tag(qn_fil)
    
    return word_term

def build_v2_nodes(cypher):
    
    # Write to Cypher File
    write_cypher(cypher, cyp_file_path)
    
    # Append to All Cypher File
    append_cypher(cypher, all_cyp_file_path)
          
    # Run Cypher Linter
    output = run_cypher_lint(cyp_file_path)
    print(output)
    
#     # Extract and parse the parse tree
#     parse_tree = extract_parse_tree(output)
#     hierarchical_tree = build_hierarchy(parse_tree)
    
#     # Split into Two Parsed Trees
#     parse_tree1, parse_tree2 = split_parsed_trees(parse_tree)
    
#     # Split into Two Hierarchical Trees
#     hierarchical_tree1, hierarchical_tree2 = split_hierarchical_trees(hierarchical_tree)
#     # print(hierarchical_tree1)
    
#     # Extract Properties
#     tree1_prop = find_label_type(hierarchical_tree1, "property")
#     tree2_prop = find_label_type(hierarchical_tree2, "property")

#     # Extract Identifiers
#     tree1_identifier = find_label_type(hierarchical_tree1, "identifier")
#     tree2_identifier = find_label_type(hierarchical_tree2, "identifier")

#     # Extract Property Names
#     tree1_prop_name = find_label_type(hierarchical_tree1, "prop name")
#     tree2_prop_name = find_label_type(hierarchical_tree2, "prop name")
    
#     # Extract Property Details
#     tree1_prop_details = extract_label_details(tree1_prop)
#     tree2_prop_details = extract_label_details(tree2_prop)

#     # Convert the Identifiers List and Property Names List into a Dictionary
#     tree1_identifier_dict = {item['id']: item['details'].replace("`", "") for item in tree1_identifier}
#     tree1_prop_name_dict = {item['id']: item['details'].replace("`", "") for item in tree1_prop_name}
#     tree2_identifier_dict = {item['id']: item['details'].replace("`", "") for item in tree2_identifier}
#     tree2_prop_name_dict = {item['id']: item['details'].replace("`", "") for item in tree2_prop_name}
    
#     # Extract the Properties from Both Trees
#     tree1_prop_list = substitute_property_details(tree1_prop_details, tree1_identifier_dict, tree1_prop_name_dict)
#     tree2_prop_list = substitute_property_details(tree2_prop_details, tree2_identifier_dict, tree2_prop_name_dict)
    
#     # Extract the MATCH id for Both Trees
#     tree1_match_id = extract_match(parse_tree1)
#     tree2_match_id = extract_match(parse_tree2)
    
#     # Extact the Relationships from Both Trees
#     tree1_rel_list = extract_node_relationship(parse_tree1, tree1_match_id)
#     tree2_rel_list = extract_node_relationship(parse_tree2, tree2_match_id)

#     # Combine the Relationship and Properties into a Single List
#     tree1_rel_prop = tree1_rel_list + tree1_prop_list
#     tree2_rel_prop = tree2_rel_list + tree2_prop_list

#     print(f"Tree 1 Relationship and Properties: {tree1_rel_prop}")
#     print(f"Tree 2 Relationship and Properties: {tree2_rel_prop}")

for idx, row in df.iterrows():
    
    word_term = build_v1_nodes(row["question"])
    
    build_v2_nodes(row["cypher"].replace('\n', ' '))