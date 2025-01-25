from transformers import BertTokenizer, BertForTokenClassification, Trainer, TrainingArguments
import torch
from torch.utils.data import Dataset

# Define the BIO Map
label_map = {'O': 0, 'B': 1, 'I': 2}
inv_label_map = {0: 'O', 1: 'B', 2: 'I'}

class CypherDataset(Dataset):
    """
    Class function to create a custom HuggingFace dataset to include BIO tags.
    """
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
        
        # Map BIO Labels to Integer Values
        label_ids = [label_map[tag] for tag in label.split()] 
        
        # Ensure Labels Match Tokenized Input
        label_ids = label_ids + [0] * (self.max_length - len(label_ids))  
        
        # Add the Labels
        encoding['labels'] = torch.tensor(label_ids)
        
        # Create an Attention Mask 
        encoding['attention_mask'] = torch.where(encoding['input_ids'] != self.tokenizer.pad_token_id, torch.tensor(1), torch.tensor(0))
        
        return encoding

def finetune_model(model_name, questions, bio_tags):
    """
    Fine-tune the BERT model. 
    
    Args:
        model_name: The name of the BERT tokenizer and model.
        question: The list of questions to tokenize.
        bio_tags: The list of annotated BIO tags.
        
    Returns:
        final: The annotated sentence.
    """
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

def predict_bio_tags(question, model, tokenizer):
    """
    Predict the BIO tags.
    
    Args:
        question: The question to predict BIO tags from.
        model: The instantiated BERT model.
        tokenizer: The instantiated BERT tokenizer.
        
    Returns:
        final: The annotated sentence.
    """
    encoding = tokenizer(question, return_tensors='pt', padding=True, truncation=True, max_length=128)
    
    with torch.no_grad():
        outputs = model(**encoding)
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=2)
        
    predicted_tags = predictions.squeeze().tolist()
    print(predicted_tags)
    predicted_labels = [inv_label_map[tag] for tag in predicted_tags]
    
    # Remove CLS and SEP Token
    predicted_labels = predicted_labels[1:-1]
    
    return predicted_labels