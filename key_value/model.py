from transformers import BertTokenizer, BertForTokenClassification, Trainer, TrainingArguments
import torch
from torch.utils.data import Dataset
import pandas as pd

# Define the BIO Map
label_map = {'O': 0, 'B': 1, 'I': 2}

# Define the custom Dataset class
class CypherDataset(Dataset):
    def __init__(self, encodings, labels, tokenizer, max_length=128):
        self.encodings = encodings
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        encoding = {key: val[idx] for key, val in self.encodings.items()}  
        label = self.labels[idx]
        
        # Map BIO labels ('O', 'B', 'I') to integer values (0, 1, 2)
        label_ids = [label_map[tag] for tag in label.split()] 
        
        # Ensure labels match the length of the tokenized input
        label_ids = label_ids + [0] * (self.max_length - len(label_ids))  
        
        # Add the labels to the item
        encoding['labels'] = torch.tensor(label_ids)
        
        # Create an attention mask (1 for real tokens and 0 for padding tokens)
        encoding['attention_mask'] = torch.where(encoding['input_ids'] != self.tokenizer.pad_token_id, torch.tensor(1), torch.tensor(0))
        
        return encoding

def finetune_model(model_name, questions, bio_tags):
    
    # Load Pretrained BERT Tokenizer and Model
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForTokenClassification.from_pretrained(model_name, num_labels=3)  
    
    # Tokenize the Questions
    encodings = tokenizer(questions, padding='max_length', truncation=True, max_length=128, return_tensors='pt')
    
    dataset = CypherDataset(encodings, bio_tags, tokenizer)
    
    # Define Training Arguments
    training_args = TrainingArguments(
        output_dir='./results',          
        num_train_epochs=3,              
        per_device_train_batch_size=8,   
        per_device_eval_batch_size=16,   
        warmup_steps=500,                
        weight_decay=0.01,               
        logging_dir='./logs',            
        logging_steps=10,
    )

    # Initialize the Trainer
    trainer = Trainer(
        model=model,                        
        args=training_args,                  
        train_dataset=dataset,               
        eval_dataset=dataset,                
    )
    
    trainer.train()
    
    return model, tokenizer

# Function to Classify BIO Tags
def predict_bio_tags(question):
    encoding = tokenizer(question, return_tensors='pt', padding=True, truncation=True, max_length=128)
    with torch.no_grad():
        outputs = model(**encoding)
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=2)
        
    predicted_tags = predictions.squeeze().tolist()
    label_map = {0: 'O', 1: 'B', 2: 'I'}  
    predicted_labels = [label_map[tag] for tag in predicted_tags]
    
    return predicted_labels