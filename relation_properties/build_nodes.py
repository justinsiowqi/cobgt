import nltk
from nltk.corpus import stopwords
from nltk import pos_tag

import subprocess
import re
import spacy

from utils import write_cypher, append_cypher

# Define File Paths Here
cyp_file_path = "cypher.cyp"
all_cyp_file_path = "all_cypher.cyp"

# ---------- Build V1 Nodes: Remove Stopwords ----------

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
        if word.lower() not in stop_list:
            qn_list_fil.append(word)

    qn_fil = " ".join(qn_list_fil)
    return qn_fil


# ---------- Build V1 Nodes: POS Tagging and Chunking ----------

# Function to Chunk and POS Tag Sentences
def chunk_and_tag(qn_fil, return_tag=True):
    """
    Chunk and POS-tag a sentence, while keeping the integrity of people entities. 
    
    Args:
        qn_fil: The filtered natural language question with stopwords removed.
        return_tag: By default, the POS tags are returned.
    
    Returns:
        word_term: A list of words from the filtered question. Each word comes with a POS-Tag.
    """
    # Load spaCy's Transformer Model
    nlp = spacy.load('en_core_web_trf')
    
    # Tokenize the Sentence
    doc = nlp(qn_fil)
        
    # List to hold chunked words
    chunked_output = []
    i = 0
    
    # Iterate Over Tokens and Merge Person Tags
    while i < len(doc):
        token = doc[i]

        # Check for Consecutive Person Tags
        if token.ent_type_ == "PERSON":  
            person_name = token.text
            while i + 1 < len(doc) and doc[i + 1].ent_type_ == "PERSON":
                i += 1
                person_name += " " + doc[i].text 

            chunked_output.append(person_name) 
        else:
            chunked_output.append(token.text)  

        i += 1

    # Clean the Chunked Output by Keeping Only Alphanumeric
    filtered_output = [word for word in chunked_output if any(c.isalnum() for c in word)]

    # Perform POS Tagging
    pos_tags = pos_tag(filtered_output)
    
    # Convert POS Tags from Set to String
    if return_tag:
        word_term = [label + f" {tag}" for label, tag in pos_tags]
    else:
        word_term = [label for label, tag in pos_tags]
        
    return word_term

def build_v1_nodes(question):
    
    # Remove Stopwords the Question
    qn_fil = remove_stopwords(question)
    
    # Chunk and POS Tag the Question
    word_terms = chunk_and_tag(qn_fil)
    
    return word_terms


# ---------- Build V2 Nodes: Parse Cypher ----------

# Function to Parse Cypher Query
def run_cypher_lint(cyp_file_path):
    try:
        # Execute the cypher-lint command
        result = subprocess.run(
            ['cypher-lint', '-a', cyp_file_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error running cypher-lint:", e.stderr)
        return None
    

# ---------- Build V2 Nodes: Extract Nodes ----------

# Define Regex Pattern
parse_tree = []
pattern = re.compile(
    r'^@(\d+)\s+'         # @<id> followed by spaces
    r'(\d+\.\.\d+)\s+'    # <span> followed by spaces
    r'([> ]*)\s+'         # Hierarchy indicators (>, spaces) followed by spaces
    r'([\w\[\]{}: ]+)\s+' # node_type (allowing spaces) followed by spaces
    r'(.*)$'              # details (rest of the line)
)

# Function to Extract Individual Nodes from the Parsed Tree
def extract_parse_tree(output):
    for line in output.split("\n"): 
        line = line.strip()           
        match = pattern.match(line)
        if match:
            node_id, span, hierarchy, node_type, details = match.groups()
            # print(f"Node ID: {node_id}")  

            level = hierarchy.count('>') 

            node = {
                'id': int(node_id),
                'span': span,
                'level': level,
                'type': node_type.strip(),
                'details': details.strip(),
                'children': []
            }
            parse_tree.append(node)
        else:
            if line:  
                print(f"Error: Unmatched line: {line}")
    return parse_tree

# Function to Build a Hierarchical Tree from the Parsed Tree
def build_hierarchy(parse_tree):
    tree = []
    stack = []

    for node in parse_tree:
        current_level = node['level']
        node_info = {
            'id': node['id'],
            'span': node['span'],
            'type': node['type'],
            'details': node['details'],
            'children': []
        }

        if current_level == 0:
            tree.append(node_info)
            stack = [node_info]
        else:
            while len(stack) > current_level:
                stack.pop()
            if stack:
                parent = stack[-1]
                parent['children'].append(node_info)
                stack.append(node_info)
            else:
                tree.append(node_info)
                stack = [node_info]

    return tree

# Function that Splits the Parsed Tree into Two Individual Parsed Trees
def split_parsed_trees(parse_tree):
    
    # Locate the Start Statement
    item_list = []
    for item in parse_tree:
        if item["type"] == "statement":
            item_list.append(item)
    
    # Define the Start and End ID
    start_id = item_list[0]["id"]
    end_id = item_list[1]["id"]
    
    # Extract the Parsed Trees
    parse_tree1 = parse_tree[start_id:end_id]
    parse_tree2 = parse_tree[end_id:]

    # Correct the IDs and Details for Parse Tree 2
    num = len(parse_tree1)
    for item in parse_tree2:
        # Subtract num from the 'id'
        item['id'] -= num

        # Check and modify the 'details' for any occurrences of '@' followed by a number
        if '@' in item['details']:
            # Replace '@number' with '@(number - num)'
            item['details'] = re.sub(r'@(\d+)', lambda x: f'@{int(x.group(1)) - num}', item['details'])
            
    return parse_tree1, parse_tree2

# Function that Splits the Hierarchical Tree into Two Individual Hierarchical Trees
def split_hierarchical_trees(hierarchical_tree):
    hierarchical_tree1 = hierarchical_tree[0]
    hierarchical_tree2 = hierarchical_tree[1]
    
    return hierarchical_tree1, hierarchical_tree2


# ---------- Build V2 Nodes: Extract Properties ----------

# Function that Searches Hierarchical Tree for Label Types
def find_label_type(data, label_type):
    label_list = []
    for child in data.get('children', []):
        if child.get('type') == label_type:
            label_list.append(child)  
        
        label_list.extend(find_label_type(child, label_type)) 

    return label_list  

# Function to Extract the Details and Clean the String
def extract_label_details(tree_items):
    detail_list = []
    for item in tree_items:
        detail_list.append(item["details"].replace(":`", "").replace("`", ""))

    return detail_list

# Function to Substitute the Property Details Using the Identifiers Dict and Property Names Dict
def substitute_property_details(tree_prop_details, tree_identifier_dict, tree_prop_name_dict):
    prop_list = []
    for item in tree_prop_details:
        parts = item.split(".")
        for idx, part in enumerate(parts):
            if part.startswith("@"):
                part_id = int(part[1:])

                if part_id in tree_identifier_dict:
                    parts[idx] = tree_identifier_dict[part_id]
                elif part_id in tree_prop_name_dict:
                    parts[idx] = tree_prop_name_dict[part_id]

        prop_list.append(".".join(parts))

    return prop_list


# ---------- Build V2 Nodes: Extract Relationships ----------

# Function to Extract the MATCH Keyword and Item ID
def extract_match(tree):
    for item in tree:
        if item["type"] == "MATCH":
            return item["id"]

# Function to Extract the Node Relationships
def extract_node_relationship(tree, match_id):

    # Extract Match Details from Match
    match_details = re.search(r'pattern=@(\d+)', tree[match_id]["details"])
    if match_details:
        pattern_id = int(match_details.group(1))

    # Extract Pattern Details from Pattern
    pattern_details = tree[pattern_id]["details"]
    if pattern_details:
        pattern_paths_str = pattern_details.split("=")[1]
        pattern_paths_str_list = re.findall(r'\d+', pattern_paths_str)
        pattern_paths_int_list = [int(num) for num in pattern_paths_str_list]

    # Extract Pattern Path Details from Pattern Path
    rel_list = []
    for paths_id in pattern_paths_int_list:
        pattern_paths_details = tree[paths_id]["details"]
        
        # Create a Dictionary with ID and Details
        numbers = list(map(int, re.findall(r'\d+', pattern_paths_details)))

        start_id = min(numbers)
        end_id = max(numbers)

        # Add 3 to End ID as a Buffer
        id_mapping = {item['id']: item['details'].replace("`", "").replace("(", "").replace(")", "").replace("-[:", "").replace("]-", "") for item in parse_tree[start_id: end_id + 3]}

        # Function to substitute each @id with its corresponding value
        def substitute_ids(match):
            id_value = int(match.group(1))  
            return id_mapping.get(id_value, f"@{id_value}")
        
        result = re.sub(r'@(\d+)', substitute_ids, pattern_paths_details)
        result = re.sub(r'@(\d+)', substitute_ids, result)

        rel_list.append(result.replace("::", ":"))
    
    return rel_list

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
    
    return tree_rel_prop