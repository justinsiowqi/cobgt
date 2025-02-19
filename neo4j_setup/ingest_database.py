from langchain_community.graphs import Neo4jGraph

# Add File Paths Here
cypher_script_path = "movies.cypher"
credentials_file_path = "../config/neo4j-credentials-example.txt"

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
