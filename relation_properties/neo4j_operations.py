# Function to Push V1 and V2 Nodes to Neo4j
def push_nodes_to_neo4j(graph, node_list, node_type):
    
    for item in node_list:
        try:
            # Toggle Between V1 and V2 Nodes
            if node_type == 'V1':
                query = "MERGE (v:V1 {name: $name})"
            elif node_type == 'V2':
                query = "MERGE (v:V2 {name: $name})"
            
            graph.query(query, {"name": item})
            
        except Exception as e:
            print(f"Error creating node {item}: {e}")
    
    print(f"{node_type} nodes created successfully.")
            
# Function to Push V1 and V2 Relationships to Neo4j
def push_v1_v2_relationships_to_neo4j(graph, node_list1, node_list2, rel_type):
    for node1 in node_list1:
        for node2 in node_list2:
            try:
                query = f"""
                    MATCH (v1 {{name: $source}}), (v2 {{name: $target}})
                    MERGE (v1)-[r:{rel_type}]->(v2)
                """
                
                params = {"source": node1, "target": node2}
                graph.query(query, params)
            
            except Exception as e:
                print(f"Error creating relationship between {node1} and {node2}: {e}")
                
    print("V1 and V2 relationships created successfully.")
    