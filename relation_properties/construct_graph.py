import pandas as pd

from langchain_community.graphs import Neo4jGraph
from utils import read_neo4j_credentials

from build_nodes import build_v1_nodes, build_v2_nodes
from connect_nodes import connect_v1_v1_nodes, connect_v1_v2_nodes

# Read the Question Schema Relationship CSV File
df = pd.read_csv("question_schema_relationship.csv")

# Add File Paths Here
cypher_script_path = "movies.cypher"
credentials_file_path = "neo4j-credentials-example.txt"

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
    return None

# Loop Through Dataframe and Construct Graph
for idx, row in df.iterrows():
    
    # Word Term Node (V1) Building
    word_terms = build_v1_nodes(row["question"])
    
    # Relation and Properties Node (V2) Building
    relation_properties = build_v2_nodes(row["cypher"])
        
    # Plot in Neo4j
    # connect_v1_v1_nodes(word_terms, tree_rel_prop)