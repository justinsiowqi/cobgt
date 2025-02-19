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