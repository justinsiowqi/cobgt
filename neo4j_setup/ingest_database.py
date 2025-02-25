import os
import glob
from langchain_community.graphs import Neo4jGraph

# Add File Paths Here
cypher_script_path = "movies.cypher"

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

# Function to Execute Cypher Script and Create a Neo4j Database
def create_database(cypher_script_path):
    
    # Read Cypher Script
    with open(cypher_script_path, 'r') as file:
        cypher_statements = file.read().strip().split(';')

    # Remove Empty Statements
    cypher_statements = [stmt.strip() for stmt in cypher_statements if stmt.strip()]

    # Execute Cypher Statements Line by Line
    for cypher in cypher_statements:
        try:
            # Execute each Cypher statement
            graph.query(cypher)
        except Exception as e:
            print(f"Error executing statement: {cypher}")
            print(f"Error message: {str(e)}")

    print("Neo4j graph database created successfully.")

create_database("movies.cypher")