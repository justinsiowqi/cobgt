import torch
from langchain_community.graphs import Neo4jGraph

from utils import get_neo4j_credentials_path, read_neo4j_credentials
from build_nodes import build_v1_nodes, build_v2_nodes
from connect_nodes import calculate_similarity
from neo4j_operations import fetch_nodes, fetch_relationships, push_v1_qn_nodes_to_neo4j, push_qn_v1_graph_v1_relationships_to_neo4j, push_v1_nodes_with_embeddings_to_neo4j, push_v2_nodes_with_embeddings_to_neo4j, fetch_nodes_with_embeddings, fetch_embeddings_from_id, fetch_v2_nodes_with_embeddings
from model import encode_node_features, create_graph_data_object, learn_node_embeddings, split_node_embeddings

# Insert Test Question Here
sample_question = "Which films was Keanu Reeves featured in before 2003?"
threshold = 0.65

# Read the Neo4j Credentials
neo4j_credentials_path = get_neo4j_credentials_path()
creds = read_neo4j_credentials(neo4j_credentials_path)

# Extracting credentials
NEO4J_URI = creds.get("NEO4J_URI")
NEO4J_USERNAME = creds.get("NEO4J_USERNAME")
NEO4J_PASSWORD = creds.get("NEO4J_PASSWORD")

# Connect to Neo4j Graph Database
graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
)

def main():
    """
    Main function for relation properties module.
    
    """
    # ---------- Step 1: Chunk Question into Tokens and Perform POS-Tagging ----------
    qn_word_terms = build_v1_nodes(sample_question)
    
    # Fetch the Graph V1 Nodes in Neo4j
    graph_nodes = fetch_nodes(graph)

    graph_word_terms = {}
    for node in graph_nodes:
        if node["labels"] == ["V1"]:
            graph_word_terms[node["id"]] = node["name"]
    
    # Push the Question V1 Nodes into Neo4j
    qn_word_terms = push_v1_qn_nodes_to_neo4j(graph, qn_word_terms)

    # ---------- Step 2: If Token Does Not Exist in Train Data, then Compare the Similarity Score ----------
    for qn_word_id, qn_word_term in qn_word_terms.items():
        
        # Check if Tokens Exist in Train Data
        if qn_word_term not in graph_word_terms.values():
            
            # Compare Similarity Score with Nodes in the Graph
            print(f"Token {qn_word_term} does not exist in train data! Performing similarity search...")

            for graph_word_id, graph_word_term in graph_word_terms.items():  
                sim_score = calculate_similarity(qn_word_term, graph_word_term)

                # Check if Score Above Threshold
                if sim_score > threshold:
                    print(f"Similarity score between {qn_word_term} and {graph_word_term} is above threshold. Creating connection...")

                    # Create a Connection
                    push_qn_v1_graph_v1_relationships_to_neo4j(graph, graph_word_id, qn_word_id)
                    print(f"Connection between question V1 node {qn_word_id} and graph V1 node {graph_word_id} completed!!!")

                else:
                    print(f"Similarity score between {qn_word_term} and {graph_word_term} is below threshold.")
    
        else:
            print(f"Token {qn_word_term} exists in train data!")
    
    # ---------- Step 3: Feed Tokens and Current Schema into GraphSAGE Module ----------
    graph_nodes = fetch_nodes(graph)
    graph_relationships = fetch_relationships(graph)
    
    # Encode the Node Features
    node_features = encode_node_features(graph_nodes)
    
    # Create Graph Data Object
    data = create_graph_data_object(node_features, graph_relationships)
    
    # Learn the Node Embeddings
    node_embeddings = learn_node_embeddings(data)
    
    # Split into V1 and V2 Node Embeddings
    v1_id_to_emb, v2_id_to_emb = split_node_embeddings(graph_nodes, node_embeddings, node_features)
    
    # Create Node Properties for Embeddings
    push_v1_nodes_with_embeddings_to_neo4j(graph, v1_id_to_emb)
    push_v2_nodes_with_embeddings_to_neo4j(graph, v2_id_to_emb)
    
    # ---------- Step 4: Achieve the Matching Score Between Question Token and Relation Properties ----------
    
    # Fetch the Question Embeddings
    qn_embeddings = {}
    for qn_word_id, qn_word_term in qn_word_terms.items():
        qn_word_emb = fetch_embeddings_from_id(graph, qn_word_id)
        qn_embeddings[qn_word_id] = qn_word_emb
    
    # Fetch the Relation Properties Embeddings
    rel_props = fetch_v2_nodes_with_embeddings(graph)
    rel_prop_embeddings = {}
    for rel_prop in rel_props:
        rel_prop_embeddings[rel_prop["id"]] = rel_prop["embeddings"]
    
    # Convert Embeddings into Tensors
    qn_embeddings_tensor = {node_id: torch.tensor(node_emb) for node_id, node_emb in qn_embeddings.items()}  
    rel_prop_embeddings_tensor = {node_id: torch.tensor(node_emb) for node_id, node_emb in rel_prop_embeddings.items()}  
    
    # Stack the Tensors
    qn_embeddings_tensor_ids = list(qn_embeddings_tensor.keys())
    rel_prop_embeddings_tensor_ids = list(rel_prop_embeddings_tensor.keys())
    
    qn_embeddings_tensor_stack = torch.stack([qn_embeddings_tensor[qid] for qid in qn_embeddings_tensor_ids])
    rel_prop_embeddings_tensor_stack = torch.stack([rel_prop_embeddings_tensor[gid] for gid in rel_prop_embeddings_tensor_ids])

    # Calculate the Dot Product Between the Node Embeddings
    matching_matrix = torch.matmul(qn_embeddings_tensor_stack, rel_prop_embeddings_tensor_stack.t())
    
if __name__ == "__main__":
    main()