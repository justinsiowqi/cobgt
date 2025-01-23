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
    
    # Extract and parse the parse tree
    parse_tree = extract_parse_tree(output)
    hierarchical_tree = build_hierarchy(parse_tree)[0]
    
    # Extract Properties
    tree_prop = find_label_type(hierarchical_tree, "property")

    # Extract Identifiers
    tree_identifier = find_label_type(hierarchical_tree, "identifier")

    # Extract Property Names
    tree_prop_name = find_label_type(hierarchical_tree, "prop name")
    
    # Extract Property Details
    tree_prop_details = extract_label_details(tree_prop)

    # Convert the Identifiers List and Property Names List into a Dictionary
    tree_identifier_dict = {item['id']: item['details'].replace("`", "") for item in tree_identifier}
    tree_prop_name_dict = {item['id']: item['details'].replace("`", "") for item in tree_prop_name}
    tree_identifier_dict = {item['id']: item['details'].replace("`", "") for item in tree_identifier}
    tree_prop_name_dict = {item['id']: item['details'].replace("`", "") for item in tree_prop_name}
    
    # Extract the Properties from Both Trees
    tree_prop_list = substitute_property_details(tree_prop_details, tree_identifier_dict, tree_prop_name_dict)
    
    # Extract the MATCH id for Both Trees
    tree_match_id = extract_match(parse_tree)
    
    # Extact the Relationships from Both Trees
    tree_rel_list = extract_node_relationship(parse_tree, tree_match_id)

    # Combine the Relationship and Properties into a Single List
    tree_rel_prop = tree_rel_list + tree_prop_list

    print(f"Relationship and Properties: {tree_rel_prop}")

for idx, row in df.iterrows():
    
    word_term = build_v1_nodes(row["question"])
    
    build_v2_nodes(row["cypher"].replace('\n', ' '))