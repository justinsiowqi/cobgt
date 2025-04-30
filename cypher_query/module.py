import pandas as pd
import torch
from transformers import (
    T5ForConditionalGeneration, AutoTokenizer,
    DataCollatorForSeq2Seq, Trainer, TrainingArguments
)
from model import format_input, prepare_dataset, finetune_model, load_latest_checkpoint, predict_cypher

extracted_key_information = "Helen Hunt"
schema_relationships = "(:Movie)<-[:ACTED_IN]-(:Actor), Actor.name, Movie.title"
# schema_relationships = "(a:Actor)-[:ACTED_IN>]-(:Movie), d.name, a.name, (:Movie)-[<:DIRECTED]-(d:Director)"
question = "Which movies include Helen Hunt as part of the cast?"

# Define the Model Name
MODEL_NAME = "t5-small"

# Read the Input Sequence Dataframe
df = pd.read_csv("../data/processed/gemini_sequence.csv").head(2)

# Prepare the Dataset
ds = prepare_dataset(df)

# Load Pretrained Tokenizer and Model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)

# Finetune the Model
model, tokenizer = finetune_model(ds, tokenizer, model)

# 1) Load the Latest Checkpoint (model + tokenizer)
checkpoint = load_latest_checkpoint()
tokenizer  = AutoTokenizer.from_pretrained(checkpoint)
model      = T5ForConditionalGeneration.from_pretrained(checkpoint)

# 2) Move model to device & set eval mode
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

# Run Inference
input_sequence = format_input(schema_relationships, extracted_key_information, question)
final_output = predict_cypher(input_sequence, tokenizer, model)
print(final_output)