import os
import glob

import torch
import torch.nn.functional as F
import torch.optim as optim
from torch_geometric.nn.models import GraphSAGE
from torch_geometric.data import Data
from sentence_transformers import SentenceTransformer

from langchain_community.graphs import Neo4jGraph

from neo4j_operations import fetch_nodes, fetch_relationships, push_v1_nodes_with_embeddings_to_neo4j, push_v2_nodes_with_embeddings_to_neo4j

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

# Fetch the Nodes and Relationships from Neo4j
graph_nodes = fetch_nodes(graph)
graph_relationships = fetch_relationships(graph)

# Set the Torch Device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Encode the Node Name into Numeric Features
embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Create a mapping
node_features = {}
for node in graph_nodes:
    text = node['name']  
    embedding = embedding_model.encode(text)
    node_features[node['id']] = embedding

# Build the Node IDs
node_ids = sorted(node_features.keys())

# Build the Feature Matrix
x = torch.tensor([node_features[nid] for nid in node_ids], dtype=torch.float)

id_to_idx = {nid: i for i, nid in enumerate(node_ids)}

# Create a List of Relationships
relationship_idx_list = []
for relationship in graph_relationships:
    src, tgt = relationship['source'], relationship['target']
    if src in id_to_idx and tgt in id_to_idx:
        relationship_idx_list.append([id_to_idx[src], id_to_idx[tgt]])

# Convert the Edges into Tensor
relationship_index = torch.tensor(relationship_idx_list, dtype=torch.long).t().contiguous()

# Create the Torch Geometric Data Object.
data = Data(x=x, edge_index=relationship_index)

# Gather Some Statistics
print(data)
print('=============================================================')
print(f'Number of nodes: {data.num_nodes}')
print(f'Number of edges: {data.num_edges}')
print(f'Average node degree: {data.num_edges / data.num_nodes:.2f}')
print(f'Has isolated nodes: {data.has_isolated_nodes()}')
print(f'Has self-loops: {data.has_self_loops()}')
print(f'Is undirected: {data.is_undirected()}')

# Instantiate the Model
model = GraphSAGE(data.num_node_features, hidden_channels=64, num_layers=3).to(device)
model

# Perform Forward Pass and Get Embeddings
model.eval()
with torch.no_grad():
    node_embeddings = model(data.x, data.edge_index)

print("Shape of node embeddings:", node_embeddings.shape)

# Match the Embeddings to Each Node ID
id_to_emb = {}
for id in id_to_idx:
    for emb in node_embeddings:
        id_to_emb[id] = emb

# Split the Embeddings Dictionary into V1 and V2 Nodes
v1_node_ids = []
v2_node_ids = []

for node in graph_nodes:
    if node["labels"] == ["V1"]:
        v1_node_ids.append(node["id"])
    if node["labels"] == ["V2"]:
        v2_node_ids.append(node["id"])
        
v1_id_to_emb = {}
v2_id_to_emb = {}

for node_id, node_embeddings in id_to_emb.items():
    if node_id in v1_node_ids:
        v1_id_to_emb[node_id] = node_embeddings
    if node_id in v2_node_ids:
        v2_id_to_emb[node_id] = node_embeddings

# Create Node Properties for Embeddings
push_v1_nodes_with_embeddings_to_neo4j(graph, v1_id_to_emb)
push_v2_nodes_with_embeddings_to_neo4j(graph, v2_id_to_emb)

