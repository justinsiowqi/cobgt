import pandas as pd
from sentence_transformers import SentenceTransformer

def calculate_similarity(word_term1_notag, word_term2_notag):
    
    # Download the MiniLM Model (Highest Accuracy)
    model = SentenceTransformer("all-mpnet-base-v2")
    
    # Encode Each Word in the Word Term No Tag List
    word_term1_embeddings = {}
    for word in word_term1_notag:
        word_term1_embeddings[word] = model.encode(word)

    word_term2_embeddings = {}
    for word in word_term2_notag:
        word_term2_embeddings[word] = model.encode(word)
    
    # Compare Each Word and Get the Similarity Scores
    sim_scores = []
    for word1, embedding1 in word_term1_embeddings.items():
        for word2, embedding2 in word_term2_embeddings.items():
            score = model.similarity(embedding1, embedding2).item()
            sim_scores.append((word1, word2, score))
        
    return sim_scores

def extract_similar_words(sim_scores, threshold=0.65):

    # Create a Dataframe
    df = pd.DataFrame(sim_scores, columns=["Question 1", "Question 2", "Similarity_Score"])
    
    # Extract Word Terms Above Threshold
    df["Above_Threshold"] = df["Similarity_Score"] > threshold
    filtered_df = df[df["Above_Threshold"] == True].drop(columns=["Above_Threshold"])
    
    sim_words = filtered_df.to_dict("records")
    
    return sim_words