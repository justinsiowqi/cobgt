import subprocess
import re
import json

# ---------- Step 1: Remove Stopwords ----------

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

cyp_file = '../sample.cyp'
output = run_cypher_lint(cyp_file)
if output:
    print(output)
    

# ---------- Step 2: Extract Nodes ----------

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


# Extract and parse the parse tree
parse_tree = extract_parse_tree(output)
hierarchical_tree = build_hierarchy(parse_tree)
print(json.dumps(hierarchical_tree, indent=2))

# Split the Parsed Trees into Two Sub Trees
item_list = []
for item in parse_tree:
    if item["type"] == "statement":
        item_list.append(item)
        
print(item_list)

start_id = item_list[0]["id"]
end_id = item_list[1]["id"]

# Extract Parse Tree 1
parse_tree1 = parse_tree[start_id:end_id]

# Extract Parse Tree 2
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

# Extract the Hierarchical Trees
hierarchical_tree1 = hierarchical_tree[0]
hierarchical_tree2 = hierarchical_tree[1]


# ---------- Step 3: Extract Properties ----------

# Function that Searches Hierarchical Tree for Label Types
def find_label_type(data, label_type):
    label_list = []
    for child in data.get('children', []):
        if child.get('type') == label_type:
            label_list.append(child)  
        
        label_list.extend(find_label_type(child, label_type)) 

    return label_list  

# Extract Properties
tree1_prop = find_label_type(hierarchical_tree1, "property")
tree2_prop = find_label_type(hierarchical_tree2, "property")

# Extract Identifiers
tree1_identifier = find_label_type(hierarchical_tree1, "identifier")
tree2_identifier = find_label_type(hierarchical_tree2, "identifier")

# Extract Property Names
tree1_prop_name = find_label_type(hierarchical_tree1, "prop name")
tree2_prop_name = find_label_type(hierarchical_tree2, "prop name")

# Function to Extract the Details and Clean the String
def extract_label_details(tree_items):
    detail_list = []
    
    for item in tree_items:
        detail_list.append(item["details"].replace(":`", "").replace("`", ""))

    return detail_list

# Extract Property Details
tree1_prop_details = extract_label_details(tree1_prop)
tree2_prop_details = extract_label_details(tree2_prop)

# Convert the Identifiers List and Property Names List into a Dictionary
tree1_identifier_dict = {item['id']: item['details'].replace("`", "") for item in tree1_identifier}
tree1_prop_name_dict = {item['id']: item['details'].replace("`", "") for item in tree1_prop_name}

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

# Extract the Properties from Both Trees
tree1_prop_list = substitute_property_details(tree1_prop_details, tree1_identifier_dict, tree1_prop_name_dict)
tree2_prop_list = substitute_property_details(tree2_prop_details, tree2_identifier_dict, tree2_prop_name_dict)


# ---------- Step 4: Extract Relationships ----------

# Function to Extract the MATCH Keyword and Item ID
def extract_match(tree):
    for item in tree:
        if item["type"] == "MATCH":
            return item["id"]
        
# Extract the MATCH id for Both Trees
tree1_match_id = extract_match(parse_tree1)
tree2_match_id = extract_match(parse_tree2)

# Function to Extract the Node Relationships
def extract_node_relationship(tree, match_id):
    node_children = []

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
        pattern_paths_details_str_list = re.findall(r'\d+', pattern_paths_details)
        pattern_paths_details_int_list = [int(num) for num in pattern_paths_details_str_list]
        
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

# Extact the Relationships from Both Trees
tree1_rel_list = extract_node_relationship(parse_tree1, tree1_match_id)
tree2_rel_list = extract_node_relationship(parse_tree2, tree2_match_id)

# Combine the Relationship and Properties into a Single List
tree1_rel_prop = tree1_rel_list + tree1_prop_list
tree2_rel_prop = tree2_rel_list + tree2_prop_list

print(f"Tree 1 Relationship and Properties: {tree1_rel_prop}"
print(f"Tree 2 Relationship and Properties: {tree2_rel_prop}"