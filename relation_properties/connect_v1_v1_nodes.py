import os
import networkx as nx
import matplotlib.pyplot as plt

import pandas as pd
from sentence_transformers import SentenceTransformer

# Define Path
SAVE_DIR = "visuals"

# Function to Calculate Similarity Score Based on Word Embeddings
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

# Function to Extract Similar Words Based on Similarity Score Threshold
def extract_similar_words(sim_scores, threshold=0.65):

    # Create a Dataframe
    df = pd.DataFrame(sim_scores, columns=["Question 1", "Question 2", "Similarity_Score"])
    
    # Extract Word Terms Above Threshold
    df["Above_Threshold"] = df["Similarity_Score"] > threshold
    filtered_df = df[df["Above_Threshold"] == True].drop(columns=["Above_Threshold"])
    
    sim_words = filtered_df.to_dict("records")
    
    return sim_words

# Function to Connect Two NetworkX Graphs
def connect_graphs(G1, sim_words):
    for word_pair in sim_words:
        G1.add_edge(word_pair["Question 1"], word_pair["Question 2"])
    
# Complex Plotting Function to Combine Two NetworkX Graphs
def complex_plot(G1, G2, word_term1_rev, rel_prop1_rev, word_term2_rev, rel_prop2_rev, filename):
    
    # Define positions for both graphs
    pos1 = {node: (0, idx) for idx, node in enumerate(word_term1_rev)}  
    pos2 = {node: (1, idx) for idx, node in enumerate(word_term2_rev)}  

    # Now, place the rel_prop nodes outward
    pos1.update({node: (1, idx + len(word_term1_rev)) for idx, node in enumerate(rel_prop1_rev)})  
    pos2.update({node: (2, idx + len(word_term2_rev)) for idx, node in enumerate(rel_prop2_rev)})

    # Combine Graph Positions
    pos = {**pos1, **pos2}

    plt.figure(figsize=(12, 8))

    # Draw Both Graphs
    nx.draw(G1, pos=pos, with_labels=True, node_size=3000, node_color='lightblue', font_size=10, font_color='black', font_weight='bold', arrows=True)
    nx.draw(G2, pos=pos, with_labels=True, node_size=3000, node_color='lightgreen', font_size=10, font_color='black', font_weight='bold', arrows=True)

    # Customize Plot and Show
    plt.axis('off') 
    
    # Create the Directory
    filepath = os.path.join(SAVE_DIR, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    plt.savefig(filepath)