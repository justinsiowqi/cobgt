from connect_nodes import calculate_similarity, extract_similar_words

# Function to Push V1 Nodes to Neo4j
def push_v1_nodes_to_neo4j(graph, node_list, question_id):
    
    for item in node_list:
        try:
            query = "MERGE (v:V1 {name: $name, question_id: $question_id})"           
            params = {"name": item, "question_id": question_id}
            graph.query(query, params)
            
        except Exception as e:
            print(f"Error creating V1 node {item}: {e}")
    
    print("V1 nodes created successfully.")
    
# Function to Push V2 Nodes to Neo4j
def push_v2_nodes_to_neo4j(graph, node_list, question_id):
    
    for item in node_list:
        try:
            query = "MERGE (v:V2 {name: $name, question_id: $question_id})"
            params = {"name": item, "question_id": question_id}
            graph.query(query, params)
            
        except Exception as e:
            print(f"Error creating V2 node {item}: {e}")
    
    print("V2 nodes created successfully.")
            
# Function to Push V1 and V2 Relationships to Neo4j
def push_v1_v2_relationships_to_neo4j(graph, v1_nodes, v2_nodes):
    for node1 in v1_nodes:
        for node2 in v2_nodes:
            try:
                query = """
                    MATCH (v1 {name: $source}), (v2 {name: $target})
                    MERGE (v1)-[r: V1_V2_CONNECTION]-(v2)
                """
                
                params = {"source": node1, "target": node2}
                graph.query(query, params)
            
            except Exception as e:
                print(f"Error creating relationship between V1 node {node1} and V2 node {node2}: {e}")
                
    print("V1 and V2 relationships created successfully.")

# Function to Push V1 and V1 Relationships to Neo4j
def push_v1_v1_relationships_to_neo4j(graph, node_list, question_id):
    
    # Fetch All the V1 Nodes from Neo4j
    existing_v1_nodes_names = []
    try:
        query = f"""
            MATCH (v1: V1) WHERE v1.question_id <> {question_id} RETURN v1
        """
        existing_v1_nodes = graph.query(query)
        existing_v1_nodes_names = [item["v1"]["name"] for item in existing_v1_nodes]

    except Exception as e:
        print(f"Error fetching list of existing nodes: {e}")        
    
    # Encode and Calculate Similarity Scores
    sim_scores = calculate_similarity(node_list, existing_v1_nodes_names)
    
    # Extract Similar Word Terms Above the 0.65 Threshold
    sim_words = extract_similar_words(sim_scores)
    print(f"Text Similarity Score > 0.65: {sim_words}")
    
    # Prevents Node from Self-Connecting
    sim_words = [sw for sw in sim_words if sw["Question 1"] != sw["Question 2"]]
    
    # Connect All the V1 Nodes Above the 0.65 Threshold
    for sim_word in sim_words:
        try:
            query = """
                MATCH (v1q1 {name: $source}), (v1q2 {name: $target})
                MERGE (v1q1)-[r:V1_V1_CONNECTION]-(v1q2)
            """
            
            params = {"source": sim_word["Question 1"], "target": sim_word["Question 2"]}
            graph.query(query, params)

        except Exception as e:
            print(f"Error creating relationship between v1 node {sim_word['Question 1']} and v1 node {sim_word['Question 2']}: {e}")
    
    print("V1 and V1 relationships created successfully.")