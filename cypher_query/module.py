from transformers import T5Tokenizer, T5ForConditionalGeneration
from model import format_input, predict_cypher

extracted_key_information = "Helen Hunt"
schema_relationships = "(:Movie)<-[:ACTED_IN]-(:Actor), Actor.name, Movie.title"
# schema_relationships = "(a:Actor)-[:ACTED_IN>]-(:Movie), d.name, a.name, (:Movie)-[<:DIRECTED]-(d:Director)"
question = "Which movies include Helen Hunt as part of the cast?"

# # Define the Input Sequence
R = schema_relationships  
K = extracted_key_information        
Q = question  

tokenizer = T5Tokenizer.from_pretrained("google-t5/t5-small")
model = T5ForConditionalGeneration.from_pretrained("google-t5/t5-small")

# Predict the Cypher Query
cypher_query = predict_cypher(tokenizer, model, R, K, Q)
print(cypher_query)