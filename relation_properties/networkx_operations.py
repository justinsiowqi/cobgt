import os
import networkx as nx
import matplotlib.pyplot as plt

from connect_nodes import calculate_similarity, extract_similar_words

# Define Path
SAVE_DIR = "visuals"


# ---------- Build NetworkX Graph ----------

# Function to Connect Two NetworkX Graphs
def connect_graphs(G1, sim_words):
    for word_pair in sim_words:
        G1.add_edge(word_pair["Question 1"], word_pair["Question 2"])
    
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


# ---------- Plot NetworkX Graph  ----------

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


# ---------- Build + Plot V1 and V2 Connections ----------
    
# Function to Create V1 and V2 Connections in NetworkX
def create_v1_v2_connection_in_networkx(word_term, tree_rel_prop):
    
    # Reverse the List so the Plot Shows Rightside Up
    word_term_rev = word_term[::-1]
    rel_prop_rev = tree_rel_prop[::-1]
    
    # Construct the Graphs for Both Questions and Cypher Statements
    G1 = construct_graph(word_term_rev, rel_prop_rev)
    
    # Plot Graph 1
    custom_plot(G1, word_term_rev, rel_prop_rev, "v1_v1_connection.png")
    
    return G1
    

# ---------- Build + Plot V1 and V1 Connections ----------

# Function to Create V1 and V1 Connections in NetworkX
def create_v1_v1_connection_in_networkx():
    
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