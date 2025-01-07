import os
import networkx as nx
import matplotlib.pyplot as plt

# Define Path
SAVE_DIR = "visuals"

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