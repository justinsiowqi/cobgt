import os
import glob
import pandas as pd

from langchain_community.graphs import Neo4jGraph

from build_nodes import build_v1_nodes, build_v2_nodes
from networkx_operations import create_v1_v2_connection_in_networkx
from neo4j_operations import push_v1_nodes_to_neo4j, push_v2_nodes_to_neo4j, push_v1_v2_relationships_to_neo4j, push_v1_v1_relationships_to_neo4j

# Read the Question Schema Relationship CSV File
df = pd.read_csv("question_schema_relationship.csv")

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

# Function to Fetch All Word Terms
def fetch_all_word_terms():
    
    all_word_terms = []
    for idx, row in df.iterrows():
        word_terms = build_v1_nodes(row["question"])
        all_word_terms += word_terms 
        
    return all_word_terms

# Function to Fetch the Schema
def fetch_schema():
    schema = graph.schema
    
    return schema

# Loop Through Dataframe and Construct Graph
for idx, row in df.iterrows():
    
    # Word Term Node (V1) Building
    word_terms = build_v1_nodes(row["question"])
    
    # Relation and Properties Node (V2) Building
    relation_properties = build_v2_nodes(row["cypher"])
    
    # Connect V1 and V1 Nodes
    G = create_v1_v2_connection_in_networkx(word_terms, relation_properties)
    
    # Construct V1 and V2 Nodes in Neo4j
    push_v1_nodes_to_neo4j(graph, word_terms, row["question_id"])
    push_v2_nodes_to_neo4j(graph, relation_properties, row["question_id"])
    
    # Construct V1 and V2 Relationships in Neo4j
    push_v1_v2_relationships_to_neo4j(graph, word_terms, relation_properties)
    
    # # Construct V1 and V1 Relationships in Neo4j
    push_v1_v1_relationships_to_neo4j(graph, word_terms, row["question_id"])