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
                    MERGE (v1)-[r: HAS_V2]->(v2)
                """
                
                params = {"source": node1, "target": node2}
                graph.query(query, params)
            
            except Exception as e:
                print(f"Error creating relationship between V1 node {node1} and V2 node {node2}: {e}")
                
    print("V1 and V2 relationships created successfully.")

# # Function to Push V1 and V1 Relationships to Neo4j
# def push_v1_v1_relationships_to_neo4j(graph, node_list1, node_list2, rel_type):
    
#     # Encode and Calculate Similarity Scores
#     sim_scores = calculate_similarity(word_term1, word_term2)
    
#     # Extract Similar Word Terms Above 0.65 Threshold
#     sim_words = extract_similar_words(sim_scores)
#     print(f"Text Similarity Score > 0.65: {sim_words}")
    
#     try:
#         query = f"""
#             MATCH (v1 {{name: $source}}), (v2 {{name: $target}})
#             MERGE (v1)-[r:{rel_type}]->(v2)
#         """
        
#         params = {"source": node1, "target": node2}
#         graph.query(query, params)

#     except Exception as e:
#         print(f"Error creating relationship between {node1} and {node2}: {e}")
    
#     print("V1 and V1 relationships created successfully.")