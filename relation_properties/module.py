import os
import glob

from langchain_community.graphs import Neo4jGraph

from build_nodes import build_v1_nodes, build_v2_nodes
from connect_nodes import calculate_similarity
from neo4j_operations import fetch_nodes, push_v1_qn_nodes_to_neo4j, push_qn_v1_graph_v1_relationships_to_neo4j

sample_question = "Which films was Keanu Reeves featured in before 2003?"
threshold = 0.65

# Function to get the Neo4j Credentials File Path 
def get_neo4j_credentials_path(config_folder="config"):
    """
    Automatically find the neo4j credentials file in the given config folder.
    
    Returns:
        The path to the credentials file.
    """
    # Get the Path to the Config Folder
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    config_folder = os.path.join(parent_dir, "config")
    
    pattern = os.path.join(config_folder, "Neo4j-*.txt")
    files = glob.glob(pattern)
    
    if not files:
        raise FileNotFoundError(
            f"No neo4j credentials file found in '{config_folder}' matching pattern 'Neo4j-*.txt'."
        )
    
    # Choose the Most Recent File
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]

# Function to Read and Extract From Neo4j Credentials File
def read_neo4j_credentials(file_path):
    """
    Read a Neo4j credentials file and extract its contents.
    
    Args:
        file_path: The file path for the Neo4j credentials txt file.
        
    Returns:
        credentials: A dictionary containing the Neo4j URI, username, instance ID and instance name.
    """
    credentials = {}
    with open(file_path, 'r') as f:
        for line in f:
            # Skip comment lines
            if line.startswith("#") or not line.strip():
                continue
            key, value = line.strip().split('=', 1)
            credentials[key] = value
    return credentials

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
    # Step 1: Chunk Question and Perform POS-Tagging
    qn_word_terms = build_v1_nodes(sample_question)
    
    # Fetch the Graph V1 Nodes in Neo4j
    graph_nodes = fetch_nodes(graph)

    graph_word_terms = {}
    for node in graph_nodes:
        if node["labels"] == ["V1"]:
            graph_word_terms[node["id"]] = node["name"]
    
    # Push the Question V1 Nodes into Neo4j
    qn_word_terms = push_v1_qn_nodes_to_neo4j(graph, qn_word_terms)

    # Step 2: Check if Tokens Exist in Train Data
    for qn_word_id, qn_word_term in qn_word_terms.items():
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
                    print("Completed!!!")

                else:
                    print(f"Similarity score between {qn_word_term} and {graph_word_term} is below threshold.")

        else:
            print(f"Token {qn_word_term} exists in train data!")
    
if __name__ == "__main__":
    main()