import pandas as pd

from langchain_community.graphs import Neo4jGraph
from utils import read_neo4j_credentials

from build_nodes import build_v1_nodes, build_v2_nodes
from networkx_operations import create_v1_v2_connection_in_networkx
from neo4j_operations import push_nodes_to_neo4j, push_v1_v2_relationships_to_neo4j

# Read the Question Schema Relationship CSV File
df = pd.read_csv("question_schema_relationship.csv")

# Add File Paths Here
credentials_file_path = "../config/Neo4j-719efdf2-Created-2025-02-21.txt"

# Read the Neo4j Credentials
creds = read_neo4j_credentials(credentials_file_path)

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
    push_nodes_to_neo4j(graph, word_terms, "V1")
    push_nodes_to_neo4j(graph, relation_properties, "V2")
    
    # Construct V1 and V2 Relationships in Neo4j
    push_v1_v2_relationships_to_neo4j(graph, word_terms, relation_properties, "HAS_V2")
    
    # # Construct V1 and V1 Relationships in Neo4j
    # create_v1_v1_relationships(graph, word_terms1, word_term2, "HAS_V1")