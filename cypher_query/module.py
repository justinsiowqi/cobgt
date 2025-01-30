from model import predict_cypher

extracted_key_information = "Helen Hunt"
schema_relationships = "(:Movie)<-[:ACTED_IN]-(:Actor), Actor.name, Movie.title"
question = "Which movies include Helen Hunt as part of the cast?"

# Define the Input Sequence
input_sequence = f"<CLS>With this information: {schema_relationships} <SEP>Key value: {extracted_key_information} <SEP>Convert this to Cypher query: {question}<EOS>"
print(f"Input Sequence: {input_sequence}")

# Predict the Cypher Query
cypher_query = predict_cypher(input_sequence)