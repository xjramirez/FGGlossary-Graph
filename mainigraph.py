import numpy as np
import requests
import json
import re
import igraph as ig
import leidenalg as la
import matplotlib
import matplotlib.pyplot as plt
import scipy as sp
import time
import random

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
    f = open("key.txt", 'w')
    for i in range(0, len(nodeArray)):
        f.write(str(i) + " : " + nodeArray[i] + "\n")
        labels[i] = nodeArray[i]
        term_sum = 0
        for entry in adjacencyMatrix:
            term_sum += entry[i]
        node_sizes.append(term_sum*10)
    f.close()

    
    start = time.time()

    # Create graph, A.astype(bool).tolist() or (A / A).tolist() can also be used.
    g = ig.Graph.Adjacency((np_adjacency_matrix > 0).tolist())

    # Add edge weights and node labels.
    ###g.es['weight'] = A[A.nonzero()]

    g.vs['label'] = list(labels.values())  # or a.index/a.columns

    deg = [6 + (degree**(1/2)) for degree in g.indegree()]

    random.seed(1)
    partition = la.find_partition(g, la.ModularityVertexPartition, seed=1)
    
    
    layout = g.layout_drl()
    #layout = layout.scale(1)
    
    

    if True:    
        fig = plt.figure(figsize=(100,100))
        
        #ig.plot(g, layout=layout, target=fig.add_subplot(), vertex_size=deg, edge_width=0.1, edge_arrow_size=.1, margin=(1,1,1,1))
        ig.plot(partition, layout=layout, target=fig.add_subplot(), vertex_size=deg, edge_width=0.1, edge_arrow_size=.1)

        plt.show()
        fig.savefig("leidenfancy_notext_seeded13.png")
    end = time.time()

    print("Drawing took " + str(end-start) + "s")

    #print(partition.membership)
    community_dict = {key: [] for key in list(range(0,max(partition.membership)+1))}
    print(partition.summary)
    k = 0
    for communitynum in partition.membership:
        community_dict[communitynum].append(labels[k])
        k+=1
    
    #print(community_dict)

    #combo = g.vs.find(label="combo")
    #print(combo.attribute_names())

    f = open("communitykey.txt", 'w')
    for i in range(0,20):
        f.write(str(i) + " : " + ",".join(str(element) for element in community_dict[i]) + "\n")
    f.close()


main()