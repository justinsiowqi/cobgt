from transformers import T5Tokenizer, T5ForConditionalGeneration

MODEL_NAME = "google-t5/t5-small"

# Function to Predict the Cypher Query
def predict_cypher(input_sequence):
    
    tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
    model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)

    input_ids = tokenizer(input_sequence, return_tensors="pt").input_ids

    outputs = model.generate(input_ids)
    cypher_query = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return cypher_query
