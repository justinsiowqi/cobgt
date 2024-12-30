import os
import warnings
from typing import List, Union
from dotenv import load_dotenv

import re
import pandas as pd

from langchain.chains.graph_qa.cypher_utils import CypherQueryCorrector, Schema
from langchain_community.graphs import Neo4jGraph
from langchain_core.messages import (
    AIMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.runnables import RunnablePassthrough
from langchain_google_vertexai import ChatVertexAI

warnings.filterwarnings('ignore')

# Insert Credentials Here
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""
MODEL_NAME = "gemini-1.5-pro"
DEMO_URL = "neo4j+s://demo.neo4jlabs.com"

# Instantiate Language Model
llm = ChatVertexAI(model_name=MODEL_NAME)

system = """Given an input question, convert it to a Cypher query.
To translate a question into a Cypher query, please follow these steps:

1. Carefully analyze the provided graph schema to understand what nodes, relationships, and properties are available. Pay attention to the node labels, relationship types, and property keys.
2. Identify the key entities and relationships mentioned in the natural language question. Map these to the corresponding node labels, relationship types, and properties in the graph schema.
3. Think through how to construct a Cypher query to retrieve the requested information step-by-step. Focus on:
   - Identifying the starting node(s) 
   - Traversing the necessary relationships
   - Filtering based on property values
   - Returning the requested information
Feel free to use multiple MATCH, WHERE, and RETURN clauses as needed.
4. Explain how your Cypher query will retrieve the necessary information from the graph to answer the original question. Provide this explanation inside <explanation> tags.
5. Once you have finished explaining, construct the Cypher query inside triple backticks ```cypher```.

Remember, the goal is to construct a Cypher query that will retrieve the relevant information to answer the question based on the given graph schema.
Carefully map the entities and relationships in the question to the nodes, relationships, and properties in the schema.
Additional instructions:
1. **Array Length**: Always use `size(array)` instead of `length(array)` to get the number of elements in an array.
2. **Implicit aggregations**: Always use intermediate WITH clause when performing aggregations
3. **Target Neo4j version is 5**: Use Cypher syntax for Neo4j version 5 and above. Do not use any deprecated syntax.
"""

# Generate Cypher statement based on natural language input
cypher_template = """Based on the Neo4j graph schema below, write a Cypher query that would answer the user's question:
{schema}

Question: {question}"""  # noqa: E501

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
    | StrOutputParser()
)

# Read the Generated Questions CSV File
questions = pd.read_csv("gemini_questions.csv")

# Read the Schema CSV File
schemas = pd.read_csv('text2cypher_schemas.csv')
schemas.head()
schema_dict = {}
for i, row in schemas.iterrows():
    schema_dict[row['database']] = row['schema']
    
# Extract from the CSV File
def extract_cypher(text):
    # Adjust pattern to capture after ```cypher and spans multiple lines until ```
    pattern = r"```cypher\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)

    if match:
        # Return the extracted text if triple backticks are present
        return match.group(1).strip()
    else:
        # Return the original text if triple backticks are not present
        return None

def extract_explanation(text):
    pattern = re.compile(r'<explanation>(.*?)</explanation>', re.DOTALL)
    match = pattern.search(text)
    if match:
        explanation_content = match.group(1).strip()
        return explanation_content
    else:
        return None
    
# Generate the Cypher Statements
print("Print in Multiples of 50 of Cypher Completed")

cypher_responses = []
for i, row in questions.iterrows():
    if i % 50 == 0:
        print(i)
    schema = schema_dict[row["database"]]
    try:
        output = cypher_response.invoke({"question": row["question"], "schema": schema})
        cypher_responses.append(
            {
                "question": row["question"],
                "database": row["database"],
                "output": output,
                "type": row["type"],
                "cypher": extract_cypher(output),
                "explanation": extract_explanation(output)
            }
        )
    except Exception as e:
        output = cypher_response.invoke({"question": row["question"], "schema": schema})
        cypher_responses.append(
            {
                "question": row["question"],
                "database": row["database"],
                "output": output,
                "type": row["type"],
                "cypher": extract_cypher(output),
                "explanation": extract_explanation(output)
            }
        )

# Save as a Pandas Dataframe
results = pd.DataFrame.from_records(cypher_responses)

# Connect to Neo4j Graph and Test
def create_graph(database):
    return Neo4jGraph(
        url=DEMO_URL,
        username=database,
        password=database,
        database=database,
        refresh_schema=False,
        timeout=10,
    )

syntax_error = []
returns_results = []
timeouts = []
not_possible = []
last_graph = ""
for i, row in results.iterrows():
    if i % 100 == 0:
        print(i)
    
    # To avoid a new driver for every request
    if row["database"] != last_graph:
        last_graph = row["database"]
        print(last_graph)
        graph = create_graph(row["database"])
    if not isinstance(row['cypher'],str) or row["cypher"].startswith("//"):
            returns_results.append(False)
            syntax_error.append(False)
            timeouts.append(False)
            not_possible.append(True)
    else:
        not_possible.append(False)
        try:
            data = graph.query(row["cypher"])
            if data:
                returns_results.append(True)
            else:
                returns_results.append(False)
            syntax_error.append(False)
            timeouts.append(False)
        except ValueError as e:
            if "Generated Cypher Statement is not valid" in str(e):
                syntax_error.append(True)
                print(f"Syntax error in Cypher query: {e}")
            else:
                syntax_error.append(False)
                print(f"Other ValueError: {e}")
            returns_results.append(False)
            timeouts.append(False)
        except Exception as e:
            if (
                hasattr(e, 'code') and e.code
                == "Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration"
            ):
                returns_results.append(False)
                syntax_error.append(False)
                timeouts.append(True)
            else:
                returns_results.append(False)
                syntax_error.append(False)
                timeouts.append(True)
                # Some weird errors we create a new graph object
                try:
                    graph._driver.close()
                except:
                    pass
                graph = create_graph(row["database"])
                
# Close the Driver
graph._driver.close()

# Save the CSV File
results.to_csv('gemini_question_cypher.csv', index=False)

results["syntax_error"] = syntax_error
results["timeout"] = timeouts
results["returns_results"] = returns_results
results["no_cypher"] = not_possible

# Drop the Rows with Syntax Error, Timeout, Empty Results or No Cypher
ids_to_drop = []
for idx, row in results.iterrows():
    if row["syntax_error"] == True:
        ids_to_drop.append(idx)
    if row["timeout"] == True:
        ids_to_drop.append(idx)
    if row["returns_results"] == False:
        ids_to_drop.append(idx)
    if row["no_cypher"] == True:
        ids_to_drop.append(idx)

results = results.drop(ids_to_drop).reset_index(drop=True)

# Save the Filtered CSV File
results.to_csv('gemini_question_cypher_filtered.csv', index=False)