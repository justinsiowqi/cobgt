import pandas as pd

from build_nodes import build_v1_nodes, build_v2_nodes
from connect_nodes import connect_v1_v1_nodes, connect_v1_v2_nodes

# Read the Question Schema Relationship CSV File
df = pd.read_csv("question_schema_relationship.csv")

for idx, row in df.iterrows():
    
    word_terms = build_v1_nodes(row["question"])
    
    tree_rel_prop = build_v2_nodes(row["cypher"].replace('\n', ' '))
    
    connect_v1_v1_nodes(word_terms, tree_rel_prop)