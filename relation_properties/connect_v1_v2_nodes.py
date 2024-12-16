import networkx as nx
import matplotlib.pyplot as plt

# Reverse the List so the Plot Shows Rightside Up
word_term1_rev = word_term1[::-1]
rel_prop1_rev = tree1_rel_prop[::-1]

word_term2_rev = word_term2[::-1]
rel_prop2_rev = tree2_rel_prop[::-1]

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

# Construct the Graphs for Both Questions and Cypher Statements
G1 = construct_graph(word_term1_rev, rel_prop1_rev)
G2 = construct_graph(word_term2_rev, rel_prop2_rev)

# Function to Plot the NetworkX Graph as a Custom Plot
def custom_plot(G, word_term_rev, rel_prop_rev):
    pos = {node: (0, idx) for idx, node in enumerate(word_term_rev)}  
    pos.update({node: (1, idx) for idx, node in enumerate(rel_prop_rev)}) 

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color='lightblue', font_size=10, font_color='black', font_weight='bold', arrows=True)
    plt.axis('off')
    plt.show()
    
# Plot Graph 1
custom_plot(G1, word_term1_rev, rel_prop1_rev)

# Plot Graph 2
custom_plot(G2, word_term2_rev, rel_prop2_rev)