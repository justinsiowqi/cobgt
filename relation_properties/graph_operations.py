# Function to Execute Cypher Script and Create a Neo4j Database
def create_database(cypher_script_path):
    
    # Read Cypher Script
    with open(cypher_script_path, 'r') as file:
        cypher_statements = file.read().strip().split(';')

    # Remove Empty Statements
    cypher_statements = [stmt.strip() for stmt in cypher_statements if stmt.strip()]

    # Execute Cypher Statements Line by Line
    for cypher in cypher_statements:
        try:
            # Execute each Cypher statement
            graph.query(cypher)
        except Exception as e:
            print(f"Error executing statement: {cypher}")
            print(f"Error message: {str(e)}")

# Function to Create V1 Nodes in Neo4j
def create_nodes(node_list, node_type):
    
    for item in node_list:
        try:
            # Choose the appropriate label for V1 or V2
            if node_type == 'V1':
                graph.query("CREATE (v1:V1 {name: $name})", parameters={"name": item})
            elif node_type == 'V2':
                graph.query("CREATE (v2:V2 {name: $name})", parameters={"name": item})
            print(f"Node {item} created as {node_type}.")
        except Exception as e:
            print(f"Error creating node {item}: {e}")