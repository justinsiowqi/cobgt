import os
import glob

import torch
import torch.nn.functional as F
import torch.optim as optim
from torch_geometric.nn.models import GraphSAGE
from torch_geometric.data import Data

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

num_nodes = 100
feature_dim = 128

# Model instantiation:
hidden_channels = 64
num_layers = 2
out_channels = 32  # final embedding dimension

model = GraphSAGE(
    in_channels=feature_dim,
    hidden_channels=hidden_channels,
    num_layers=num_layers,
    out_channels=out_channels,  
    dropout=0.0,
    act='relu',
    jk=None  
)