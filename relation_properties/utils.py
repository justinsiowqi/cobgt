import os

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

def create_folder():
    """
    Create a folder if it doesn't exist.
    """
    # Create the Directory
    filepath = os.path.join(visuals_dir, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

def read_question_cypher(file_path):
    """
    Read question_cypher.txt file.
    
    Args:
        file_path: The file path of question_cypher.txt.
    
    Returns:
        question1: First question.
        cypher1:Cypher statement of question 1.
        question2: Second question.
        cypher2: Cypher statement of question 2.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    question1 = cypher1 = question2 = cypher2 = ""

    if len(lines) >= 4:
        question1 = lines[0].strip().replace("Question 1: ", "")
        cypher1 = lines[1].strip().replace("Cypher 1: ", "")
        question2 = lines[2].strip().replace("Question 2: ", "")
        cypher2 = lines[3].strip().replace("Cypher 2: ", "")

    return question1, cypher1, question2, cypher2

def write_cypher(cypher, file_path):
    """
    Write a Cypher statement to the cypher.cyp file.

    Args:
        cypher_statement: Cypher statement to write to the file.
        file_path: The file path of the Cypher file.
    """
    with open(file_path, 'w') as file:
        file.write(cypher + ";")

def append_cypher(cypher, file_path):
    """
    Append a Cypher statement to the cypher.cyp file.

    Args:
        cypher_statement: Cypher statement to append to the file.
        file_path: The file path of the Cypher file.
    """
    with open(file_path, 'a') as file:
        file.write(cypher + ";" + "\n")