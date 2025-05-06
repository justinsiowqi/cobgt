import os
import warnings
import json
from typing import List
import builtins

import re
import pandas as pd

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.graphs import Neo4jGraph

from utils import get_gcp_credentials_path

warnings.filterwarnings('ignore')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = get_gcp_credentials_path()

# Insert Credentials Here
MODEL_NAME = "gemini-2.0-flash"
DEMO_URL = "neo4j+s://demo.neo4jlabs.com"
DEMO_DATABASES = ["movies"]

# Instantiate Language Model
llm = ChatGoogleGenerativeAI(model=MODEL_NAME, timeout=60)

# Read the Template Questions Dataframe
question_df = pd.read_csv("../data/gemini_questions.csv")

prompt_template = """

    You are an expert Neo4j developer.  
    Given a Graph Schema, generate Cypher queries that answer each of the provided template questions.
    
    Graph Schema:
    {schema}
    
    Database:
    {database}
    
    Input:
    {input}
    
    Instructions:
    - Generate between 35 and 40 cypher queries, one for each template question.  
    - Use placeholders in square brackets matching exactly the property names, e.g. `[title]`, `[votes]`, `[roles]`, `[rating]`.
    - Ensure every Cypher query is syntactically valid and answerable using only the provided schema. 
    - Output the results as a valid JSON list where each item is an object with two keys: question and database.
    - Do not include any introductory text, explanations, or markdown formatting before or after the JSON list. Only output the JSON list itself.

    Example Input:
    [
      {{"question": "What movies feature the performance of [name]?", "database": "movies"}},
      {{"question": "Which movies were released in [released]?", "database": "movies"}}
    ]
    
    Example Output:
    [
      {{"question": "What movies feature the performance of [name]?", "database": "movies", "cypher": "MATCH (m:Movie)<-[:ACTED_IN]-(a:Actor) WHERE a.name = [name] RETURN m.title"}},
      {{"question": "Which movies were released in [released]?", "database": "movies", "cypher": "MATCH (m:Movie) WHERE m.released = [released] RETURN m.title;"}}
    ]
"""

# Define the Parser
parser = JsonOutputParser()

# Define the Prompt Template
prompt = PromptTemplate(
    template=prompt_template, 
    input_variables=["schema", "database", "input"], 
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# Instantiate Langchain
chain = prompt | llm | parser

all_cypher = []
for database in DEMO_DATABASES:
    print(f"Processing database: {database}")
    graph = Neo4jGraph(
        url=DEMO_URL,
        database=database,
        username=database,
        password=database,
        enhanced_schema=True,
        sanitize=True,
        timeout=30,
    )
    schema = graph.schema
    
    fil_question_df = question_df[question_df["database"] == database]
    json_input = fil_question_df.to_json(orient="records")
    
    try:
        cypher = chain.invoke(
            {"schema": schema, "database": database, "input": json_input}
        )
        all_cypher.extend(cypher)
    except Exception as e:
        print(f"An error occurred processing database '{database}': {e}")
    finally: 
        graph._driver.close() 
            
# Save the Dataframe
cypher_df = pd.DataFrame(all_cypher)
cypher_df.drop_duplicates(subset='question').to_csv("../data/gemini_cypher.csv", index=False)