from langchain_community.graphs import Neo4jGraph
from utils import read_neo4j_credentials

# Add File Paths Here
cypher_script_path = "movies.cypher"
credentials_file_path = "Neo4j-85978cdc-Created-2025-01-28.txt"

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

# Function to Execute Cypher Script
def execute_cypher_script(cypher_script_path):
    
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

execute_cypher_script(cypher_script_path)