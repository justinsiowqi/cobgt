def format_input(R, K, Q):
    D1 = "With this information: "
    D2 = "Key value: "
    D3 = "Convert to Cypher query: "

    input_text = (
        f"<CLS>{D1}{R} <<SEP>{D2}{K} <SEP>{D3}{Q} <EOS>"
    )
    return input_text


def predict_cypher(tokenizer, model, R, K, Q):
    """
    Generate a cypher query based on the input sequence.
    
    Args:
        input_sequence: Sequence that includes the schema relationships, extracted key information and question.
        
    Returns:
        cypher_query: The generated cypher query.
    """
    input_text = "generate Cypher: " + format_input(R, K, Q)
    
    # Tokenize with T5's special tokens
    input_ids = tokenizer(
        input_text,
        return_tensors="pt",
        max_length=512,
        truncation=True,
        add_special_tokens=True  
    ).input_ids

    outputs = model.generate(
        input_ids,
        max_new_tokens=200,  
        num_beams=5,
        early_stopping=True,
        no_repeat_ngram_size=2 
    )
    
    return tokenizer.decode(outputs[0], skip_special_tokens=True)