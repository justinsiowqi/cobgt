import os
import json
from typing import List

import re
import pandas as pd

from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.graphs import Neo4jGraph

# Insert Credentials Here
os.environ["GOOGLE_API_KEY"] = ""
MODEL_NAME = "gemini-1.5-pro"
DEMO_URL = "neo4j+s://demo.neo4jlabs.com"
DEMO_DATABASES = ["movies"]

# Instantiate Language Model
llm = ChatGoogleGenerativeAI(model=MODEL_NAME, timeout=60)

query_types = {
    "Simple Retrieval Queries": "These queries focus on basic data extraction, retrieving nodes or relationships based on straightforward criteria such as labels, properties, or direct relationships. Examples include fetching all nodes labeled as 'Person' or retrieving relationships of a specific type like 'EMPLOYED_BY'. Simple retrieval is essential for initial data inspections and basic reporting tasks. Always limit the number of results if more than one row is expected from the questions by saying 'first 3' or 'top 5' elements",
    "Complex Retrieval Queries": "These advanced queries use the rich pattern-matching capabilities of Cypher to handle multiple node types and relationship patterns. They involve sophisticated filtering conditions and logical operations to extract nuanced insights from interconnected data points. An example could be finding all 'Person' nodes who work in a 'Department' with over 50 employees and have at least one 'REPORTS_TO' relationship. Always limit the number of results if more than one row is expected from the questions by saying 'first 3' or 'top 5' elements",
    "Simple Aggregation Queries": "Simple aggregation involves calculating basic statistical metrics over properties of nodes or relationships, such as counting the number of nodes, averaging property values, or determining maximum and minimum values. These queries summarize data characteristics and support quick analytical conclusions. Always limit the number of results if more than one row is expected from the questions by saying 'first 3' or 'top 5' elements",
    "Pathfinding Queries": "Specialized in exploring connections between nodes, these queries are used to find the shortest path, identify all paths up to a certain length, or explore possible routes within a network. They are essential for applications in network analysis, routing, logistics, and social network exploration. Always limit the number of results if more than one row is expected from the questions by saying 'first 3' or 'top 5' elements",
    "Complex Aggregation Queries": "The most sophisticated category, these queries involve multiple aggregation functions and often group results over complex subgraphs. They calculate metrics like average number of reports per manager or total sales volume through a network, supporting strategic decision making and advanced reporting. Always limit the number of results if more than one row is expected from the questions by saying 'first 3' or 'top 5' elements",
    "Verbose query": "These queries are characterized by their explicit and detailed specifications about the data retrieval process and the exact information needed. They involve elaborate instructions for navigating through complex data structures, specifying precise criteria for inclusion, exclusion, and sorting of data points. Verbose queries typically require the breakdown of each step in the querying process, from the initial identification of relevant data nodes and relationships to the intricate filtering and sorting mechanisms that must be applied. Always limit the number of results if more than one row is expected from the questions by saying 'first 3' or 'top 5' elements",
    "Evaluation query": "This query type focuses on retrieving specific pieces of data from complex databases with precision. Use clear and detailed instructions to extract relevant information, such as movie titles, product names, or employee IDs, depending on the context. Always ask for a single property or item, titled intuitively based on the data retrieved (e.g., Movie Titles Featuring Tom Cruise). Limit the results to a specific number like 'first 3' or 'top 5' to keep the output concise and focused.",
    "Multi-step Queries": "Multistep queries in a graph database involve executing several operations or traversals to derive the answer. These queries typically combine different data elements by following multiple relationships and filtering nodes at various steps to reach a final result. They often require joining data from various parts of the schema, aggregating results, or applying multiple conditions to uncover complex insights that are not immediately apparent from a single node or relationship"
}

prompt_template = """Your task is to generate 100 questions that are directly related to a specific graph schema in Neo4j. Each question should target distinct aspects of the schema, such as relationships between nodes, properties of nodes, or characteristics of node types. Ensure that the questions vary in complexity, covering basic, intermediate, and advanced queries.
Imagine you are a user at a company that needs to present all the types of questions that the graph can answer.
You have to be very diligent at your job. Make sure you will accomplish a diversity of questions, ranging from various complexities.

Avoid ambiguous questions. For clarity, an ambiguous question is one that can be interpreted in multiple ways or does not have a straightforward answer based on the schema. For example, avoid asking, "What is related to this?" without specifying the node type or relationship.
Please design each question to yield a limited number of results, specifically between 3 to 10 results. This will ensure that the queries are precise and suitable for detailed analysis and training.
The goal of these questions is to create a dataset for training AI models to convert natural language queries into Cypher queries effectively.
It is vital that the database contains information that can answer the question!
Never write any assumptions, just the questions!!!
Make sure to generate 100 questions!

Make sure to create questions for the following graph schema:{input}\n 
Here are some example nodes and relationship values: {values}. 
Don't use any values that aren't found in the schema or in provided values.
{query_type}
Also, do not ask questions that there is no way to answer based on the schema or provided example values. 
Find good questions that will test the capabilities of graph answering.
The output of the should be 1 question per row. Example output format:
What movies did Tom Cruise acted in?
Which product made the most revenue?
Who is the manager of the team that completed the most projects last year?
Generated questions:"""

# Define the Prompt Template
prompt = PromptTemplate(
    input_variables=["input", "values", "query_type"], template=prompt_template
)

# Instantiate Langchain
chain = prompt | llm

# Function to Match Numbers Followed by a Dot and Additional Space at Start of String
def remove_enumeration(text):
    return re.sub(r'^\d+\.\s?', '', text).strip()

all_questions = []
for database in DEMO_DATABASES:
    print(database)
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
    for type in query_types:
        print(type)
        instructions = f"{type}: {query_types[type]}"
        # Sample values
        values = graph.query(
            """MATCH (n)
            WHERE rand() > 0.6
            WITH n LIMIT 2
            CALL {
                WITH n
                MATCH p=(n)-[*3..3]-()
                RETURN p LIMIT 1
            }
            RETURN p"""
        )

        try: # sometimes it timeouts
            questions = chain.invoke(
                {"input": schema, "query_type": instructions, "values": values}
            )
            all_questions.extend(
            [
                {"question": remove_enumeration(el), "type": type, "database": database}
                for el in questions.content.split("\n") if not "## 100" in el and el
            ]
            )
        except:
            continue

# Save the Dataframe
df = pd.DataFrame.from_records(all_questions)
df.drop_duplicates(subset='question').to_csv('gemini_questions.csv', index=False)
