from connect_nodes import calculate_similarity_between_node_lists, extract_similar_words

# Function to Fetch the Schema
def fetch_schema():
    schema = graph.schema
    
    return schema

# Function to Fetch All V1 and V2 Nodes
def fetch_nodes(graph):
    try:
        query = """
            MATCH (n)
            WHERE n:V1 OR n:V2
            RETURN elementId(n) AS id, n.question_id AS question_id, n.name AS name, labels(n) AS labels
        """
        graph_nodes = graph.query(query)
        return graph_nodes
    
    except Exception as e:
        print(f"Error fetching V1 and V2 nodes: {e}")

# Function to Fetch All V1 and V2 Nodes with Embeddings
def fetch_nodes_with_embeddings(graph):
    try:
        query = """
            MATCH (n)
            WHERE n:V1 OR n:V2
            RETURN elementId(n) AS id, n.question_id AS question_id, n.name AS name, n.embeddings AS embeddings, labels(n) AS labels
        """
        graph_nodes = graph.query(query)
        return graph_nodes
    
    except Exception as e:
        print(f"Error fetching V1 and V2 nodes: {e}")
        
def fetch_embeddings_from_id(graph, node_id):
    try:
        query = """
            MATCH (n)
            WHERE elementId(n) = $node_id
            RETURN n.embeddings AS embeddings
        """
        params = {"node_id": str(node_id)}
        node_embeddings = graph.query(query, params)
        
        return node_embeddings[0]["embeddings"]
    
    except Exception as e:
        print(f"Error fetching node embeddings: {e}")
        
# Function to Fetch All Relationships
def fetch_relationships(graph):
    try:
        query = """
            MATCH (a)-[r]->(b)
            WHERE type(r) IN ['V1_V1_CONNECTION', 'V1_V2_CONNECTION']
            RETURN elementId(a) AS source, elementId(b) AS target, type(r) AS rel_type
        """
        graph_relationships = graph.query(query)
        return graph_relationships
    
    except Exception as e:
        print(f"Error fetching relationships: {e}")
    
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

# Function to Push Question V1 Nodes to Neo4j
def push_v1_qn_nodes_to_neo4j(graph, node_list):
    node_dict = {}

    for item in node_list:
        try:
            query = """
                MERGE (v:V1 {name: $name})
                RETURN elementId(v) AS id, v.name AS name
            """
            params = {"name": item}
            result = graph.query(query, params)

            if result:
                node_dict[result[0]["id"]] = result[0]["name"]
        
        except Exception as e:
            print(f"Error creating V1 node {item}: {e}")
    
    print("V1 nodes created successfully.")
    
    return node_dict
    
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
    sim_scores = calculate_similarity_between_node_lists(node_list, existing_v1_nodes_names)
    
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
    
# Function to Push Question V1 Nodes and Graph V1 Nodes Relationships to Neo4j
def push_qn_v1_graph_v1_relationships_to_neo4j(graph, graph_node_id, qn_word_id):
    
    try:
        query = """
            MATCH (v1q1)
            WHERE elementId(v1q1) = $source
            MATCH (v1q2)
            WHERE elementId(v1q2) = $target
            MERGE (v1q1)-[:V1_V1_CONNECTION]-(v1q2)
        """

        params = {"source": graph_node_id, "target": qn_word_id}
        graph.query(query, params)

    except Exception as e:
        print(f"Error creating relationship between v1 node {graph_node_id} and v1 node {qn_word_id}: {e}")
    
# Function to Push V1 Nodes with Embeddings to Neo4j
def push_v1_nodes_with_embeddings_to_neo4j(graph, id_to_emb_dict):
    for node_id, node_embeddings in id_to_emb_dict.items():
        try:
            embeddings_list = node_embeddings.tolist()
            
            query = """
                MATCH (n:V1) 
                WHERE elementId(n) = $node_id
                SET n.embeddings = $embeddings
                RETURN n
            """
            params = {"node_id": str(node_id),  "embeddings": embeddings_list}
            graph.query(query, params)
            
        except Exception as e:
            print(f"Error updating V1 node {node_id}: {e}")
    
    print("V1 nodes with embeddings updated successfully.")
    
# Function to Push V2 Nodes with Embeddings to Neo4j
def push_v2_nodes_with_embeddings_to_neo4j(graph, id_to_emb_dict):
    for node_id, node_embeddings in id_to_emb_dict.items():
        try:
            embeddings_list = node_embeddings.tolist()
            
            query = """
                MATCH (n:V2) 
                WHERE elementId(n) = $node_id
                SET n.embeddings = $embeddings
                RETURN n
            """
            params = {"node_id": str(node_id),  "embeddings": embeddings_list}
            graph.query(query, params)
            
        except Exception as e:
            print(f"Error updating V2 node {node_id}: {e}")
    
    print("V2 nodes with embeddings updated successfully.")