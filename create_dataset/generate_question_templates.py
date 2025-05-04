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

prompt_template = """

    You are an expert Neo4j developer.  
    Given a Graph Schema, generate a set of template questions.
    
    Graph Schema:
    {schema}
    
    Database:
    {database}
    
    Instructions:
    - Generate between 35 and 40 template questions.  
    - Use placeholders in square brackets `[]` for variable parts (e.g. `[actor]`, `[year]`).
    - Ensure questions are answerable based only on the provided schema.    
    - Output the results as a valid JSON list where each item is an object with two keys: question and database.
    - Do not include any introductory text, explanations, or markdown formatting before or after the JSON list. Only output the JSON list itself.

    Example Output:
    [
      {{"question": "What movies feature the performance of [actor]?", "database": "movies"}},
      {{"question": "Can you provide a list of movies in which both [actor1] and [actor2] appear?", "database": "movies"}}
    ]
"""

# Define the Parser
parser = JsonOutputParser()

# Define the Prompt Template
prompt = PromptTemplate(
    template=prompt_template, 
    input_variables=["schema", "database"], 
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# Instantiate Langchain
chain = prompt | llm | parser

all_questions = []
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
    try:
        questions = chain.invoke(
            {"schema": schema, "database": database}
        )
        all_questions.extend(questions)
    except Exception as e:
        print(f"An error occurred processing database '{database}': {e}")
    finally: 
        graph._driver.close() 
            
# Save the Dataframe
df = pd.DataFrame(all_questions)
df.drop_duplicates(subset='question').to_csv("../data/gemini_questions.csv", index=False)