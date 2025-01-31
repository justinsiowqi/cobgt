import os
import networkx as nx
import matplotlib.pyplot as plt

import pandas as pd
from sentence_transformers import SentenceTransformer

# Define Path
SAVE_DIR = "visuals"

# Function to Calculate Similarity Score Based on Word Embeddings
def calculate_similarity(word_term1_notag, word_term2_notag):
    
    # Download the MiniLM Model
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

def connect_v1_v1_nodes(word_term, tree_rel_prop):
    
    # Reverse the List so the Plot Shows Rightside Up
    word_term_rev = word_term[::-1]
    rel_prop_rev = tree_rel_prop[::-1]
    
    # Construct the Graphs for Both Questions and Cypher Statements
    G1 = construct_graph(word_term_rev, rel_prop_rev)
    
    # Plot Graph 1
    custom_plot(G1, word_term_rev, rel_prop_rev, "graph1.png")
    
# Functiont o Construct a NetworkX Graph and Add the Relevant Node and Connections
def construct_graph(word_term_rev, rel_prop_rev):
    
    # Create an Empty Graph
    G = nx.Graph()

    # Add the Nodes to the Graph
    G.add_nodes_from(word_term_rev)
    G.add_nodes_from(rel_prop_rev)

    # Add the Connections to the Graph
    for left in word_term_rev:
        for right in rel_prop_rev:
            G.add_edge(left, right)
            
    return G

# Function to Plot the NetworkX Graph as a Custom Plot
def custom_plot(G, word_term_rev, rel_prop_rev, filename):
    pos = {node: (0, idx) for idx, node in enumerate(word_term_rev)}  
    pos.update({node: (1, idx) for idx, node in enumerate(rel_prop_rev)}) 

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color='lightblue', font_size=10, font_color='black', font_weight='bold', arrows=True)
    plt.axis('off')
    
    # plt.show()
    
    # Create the Directory
    filepath = os.path.join(SAVE_DIR, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    plt.savefig(filepath)
    
def connect_v1_v2_nodes():
    
    # Encode and Calculate Similarity Scores
    sim_scores = calculate_similarity(word_term1, word_term2)
    
    # Extract Similar Word Terms Above 0.65 Threshold
    sim_words = extract_similar_words(sim_scores)
    print(f"Text Similarity Score > 0.65: {sim_words}")
    
    # Connect the Two Sub-Graphs
    connect_graphs(G1, sim_words)
    
    # # Plot Both Connected Sub-Graphs as a Complex Plot
    # complex_plot(G1, G2, word_term1_rev, rel_prop1_rev, word_term2_rev, rel_prop2_rev, "graph1_graph2.png")
    
    print("Graph 1 connected with Graph 2 saved successfully.")