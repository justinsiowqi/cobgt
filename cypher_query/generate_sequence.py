import os
import glob
import json
import warnings

import pandas as pd
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_google_vertexai import ChatVertexAI

warnings.filterwarnings("ignore")

# Function to get the GCP Credentials File Path 
def get_gcp_credentials_path(config_folder="config"):
    """
    Automatically find the neo4j credentials file in the given config folder.
    
    Returns:
        The path to the credentials file.
    """
    # Get the Path to the Config Folder
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    config_folder = os.path.join(parent_dir, "config")
    
    pattern = os.path.join(config_folder, "*.json")
    files = glob.glob(pattern)
    
    if not files:
        raise FileNotFoundError(
            f"No gcp credentials file found in '{config_folder}'."
        )
    
    # Choose the Most Recent File
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = get_gcp_credentials_path()

# Insert Credentials Here
MODEL_NAME = "gemini-1.5-pro"

# Instantiate Language Model
llm = ChatVertexAI(model_name=MODEL_NAME)

# Read the Generated Questions Cyphers CSV File
question_cypher = pd.read_csv("../data/processed/gemini_question_cypher_filtered.csv")

system = """
    You are an expert at extracting relationship properties and key values from cypher queries.
        
    Given a natural‐language question, its Cypher translation, and an explanation, you must extract:
    1. relation_properties: each node label or relationship and the properties mentioned.
    2. key_values: each filter or argument property with its literal value.
    
    Additional instructions:
    Output ONLY a JSON object with those two fields.
    
    Example:
    Question: Which movies include Helen Hunt as part of the cast?
    Cypher: MATCH (m:Movie)<-[:ACTED_IN]-(a:Actor) WHERE a.name = "Helen Hunt" RETURN m.title
    Explanation: This query finds all movies in which Helen Hunt appears and returns their titles.\nMATCH Clause: We use MATCH (m:Movie)<-[:ACTED_IN]-(a:Actor) to locate every Movie node m that has an incoming ACTED_IN relationship from an Actor node a.\nWHERE Clause: We filter those actor nodes so that only the ones with a.name = "Helen Hunt" remain.\nRETURN Clause: We return the m.title property of each matching movie node.
    Answer:
    {{
        "relation_properties": ["(:Movie)<-[:ACTED_IN]-(:Actor)", "Actor.name", "Movie.title"], 
        "key_value": "Helen Hunt"
    }}
"""

# Generate Cypher statement based on natural language input
cypher_template = """
    Question: {question}
    Cypher: {cypher}
    Explanation: {explanation}
    
    Return JSON like:
    {{
        "relation_properties": ["(:Movie)<-[:ACTED_IN]-(:Actor)", "Actor.name", "Movie.title"], 
        "key_value": ""Helen Hunt"
    }}
"""

cypher_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",system ),
        ("human", cypher_template),
    ]
)

cypher_response = (
    cypher_prompt
    | llm
    | JsonOutputParser()
)


# Extract the Relation Properties and Key Values
question_cypher["relation_properties"] = None
question_cypher["key_values"] = None

for idx, row in question_cypher.iterrows():
    output = cypher_response.invoke(
        {
            "question": row["question"],
            "cypher": row["cypher"],
            "explanation": row["explanation"],
        }
    )
    
    # Convert to String 
    rel_list = output.get("relation_properties", [])
    kv_list  = output.get("key_values", [])

    if isinstance(rel_list, list):
        rel_str = ",".join(str(x) for x in rel_list)
    else:
        rel_str = str(rel_list)

    if isinstance(kv_list, list):
        kv_str = ",".join(str(x) for x in kv_list)
    else:
        kv_str = str(kv_list)
    
    question_cypher.loc[idx, "relation_properties"] = rel_str
    question_cypher.loc[idx, "key_values"] = kv_str
    

# Save as a Pandas Dataframe
question_cypher.to_csv("../data/processed/gemini_sequence.csv", index=False)
