import numpy as np
import requests
import json
import re
import networkx as nx
import matplotlib as plt
import matplotlib.pyplot
import scipy as sp
import time

def main():
    
    adjacencyMatrix = []
    nodeArray = []
    url = "https://glossary.infil.net/json/glossary.json"
    #print(url)
    glossary_file = requests.get(url)
    #print(type(glossary_file))
    glossary_list = glossary_file.json() #just .loads() the .text of the object you call it on lol

    links_to_dict = {}
    linked_to_from_dict = {}

    for thing in glossary_list:#[0:300]:
        links_to_dict[thing['term'].lower()] = []
        linked_to_from_dict[thing['term'].lower()] = []
        for key, val in thing.items():
            if key == 'term':
                nodeArray.append((val).lower())

    adjacencyMatrix = [[0]*len(nodeArray) for i in range(0, len(nodeArray))] #DO NOT DO [[0] *n]*n or else each row will be a reference to each other for some fucking reason

    for entry in glossary_list:#[0:300]:
        term = entry['term']
        
        entry_index = nodeArray.index(term.lower())
        
        definition = re.sub(r'([0-9A-Za-z]+)[\'`]([0-9A-Za-z]+)', r'\1'r'\2', entry['def'])
        search_result = re.findall(r"'(.*?)'", definition)
        if (search_result):
            for link in search_result:
                if link in nodeArray:
                    link_index = nodeArray.index(link)

                    links_to_dict[term.lower()].append(link)
                    linked_to_from_dict[link].append(term.lower())
                    
                    adjacencyMatrix[entry_index][link_index]+= 1

    #print(links_to_dict['runback'])
    #print(linked_to_from_dict['runback'])

    np_adjacency_matrix = np.array(adjacencyMatrix)

    node_sizes = []
    term_sum = 0
    labels = {}
    f = open("key.txt", 'a')
    for i in range(0, len(nodeArray)):
        f.write(str(i) + " : " + nodeArray[i] + "\n")
        labels[i] = nodeArray[i]
        term_sum = 0
        for entry in adjacencyMatrix:
            term_sum += entry[i]
        node_sizes.append(term_sum*10)
    f.close()

    start = time.time()
    G = nx.from_numpy_array(np_adjacency_matrix, create_using=nx.DiGraph)
    fig = plt.pyplot.figure(figsize=(75,75))

    comp = nx.community.girvan_newman(G)
    communities = tuple(sorted(c) for c in next(comp))
    print(communities)


    pos_dict = nx.nx_agraph.graphviz_layout(G, prog='neato', args='-s100')
    #modified_pos_dict = pos_dict
    """
      j = 0
    modifier = 20
    for node in pos_dict.values():
        
        modified_pos_dict[j] = (node[0]*modifier, node[1]*modifier)
        j+= 1  
    
    
    """

    
    nx.draw_networkx(G, pos = pos_dict, labels=labels, arrowsize=4, with_labels=True, ax=fig.add_subplot(), font_size=8, node_size=node_sizes, width=0.25, edge_color="#B85042", node_color="#E7E8D1")#, text_color="A7BEAE")
    if True: 
        # Save plot to file
        plt.use("Agg") 
        fig.savefig("neatrr.png")
    else:
        # Display interactive viewer
        matplotlib.pyplot.show()
    
    end = time.time()

    print("Drawing took " + str(end-start) + "s")

    





main()