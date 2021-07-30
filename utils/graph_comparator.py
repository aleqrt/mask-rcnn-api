import os
import re
import sys
import warnings
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from sklearn import preprocessing

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    # Root directory of the project
    ROOT_DIR = os.path.abspath("..")
    sys.path.append(ROOT_DIR)


################################################################################################################

def get_ax(rows=1, cols=1, size=8):
    """Return a Matplotlib Axes array to be used in
    all visualizations in the notebook. Provide a
    central point to control graph sizes.

    Change the default size attribute to control the size
    of rendered images
    """
    fig, ax = plt.subplots(rows, cols, figsize=(size * cols, size * rows))
    return fig, ax


def parser_component(facts):
    """Parsificatore del file di fatti ASP.
       Return:
           - component, lista contentente [Label, Id, Xs1, Ys1, Xd2, Yd2]
    """
    component = []
    with open(facts, 'r') as f:
        for i, line in enumerate(f):
            cmp = line.split('(')[1].split(')')[0].split(',')
            component.append([cmp[0].replace('\"', ''), int(cmp[1]),
                              int(cmp[2]), int(cmp[3]),
                              int(cmp[4]), int(cmp[5])])
    return component


def parser_neighbour(output_name):
    """Parsificatore del file di output ASP.
        
       Input:
           - file contenente il predicato posRelNet oppure posRelCad.
       Return:
           - neighbours, lista contenente [Label1, Id1, Label2, Id2, Position]
    """
    with open(output_name, 'r') as f:
        for i, line in enumerate(f):
            if i >= 2:
                neighbours = [e for e in re.findall('\((.*?)\)', line)]

    tmp = []
    for e in neighbours:
        tmp.append((e.split(',')))

    neighbour = []
    for row in tmp:
        row[0] = row[0].replace('\"', '')
        row[1] = int(row[1])
        row[2] = row[2].replace('\"', '')
        row[3] = int(row[3])
        neighbour.append(row)
    return neighbour


def checkNodeClass(green, yellow, red, max_score):
    """Funzione per verificare che ad un nodo del grafo non sia stata assegnata più di una classe
       NOTA:
           - green -> OK
           - yellow -> Forse
           - red -> NO
    """
    for key in max_score:
        for k in max_score:
            if max_score[key][0] == max_score[k][0] and max_score[key][1] > max_score[k][1]:
                del max_score[k]
                green.remove(k)

    vs_12 = [v for v in yellow if (v in green)]
    vs_13 = [v for v in red if (v in green)]
    vs_23 = [v for v in red if (v in yellow)]
    if vs_12:
        for v in vs_12:
            yellow.remove(v)
    if vs_13:
        for v in vs_13:
            red.remove(v)
    if vs_23:
        for v in vs_23:
            red.remove(v)
    return yellow, red


def removeDuplicates(lst):
    return list(set([i for i in lst]))


################################################################################################################
# Main function

def main():
    """Main function for graph comparator
    """
    resoner_dir = os.path.join("reasoner")
    graph_dir = os.path.join(resoner_dir, "graph")
    net_dir = os.path.join(resoner_dir, "net")
    cad_dir = os.path.join(resoner_dir, "cad")

    facts_net = os.path.join(net_dir, "IMG_4416_warp_net.asp")  # File contenente il predicato net
    output_net = os.path.join(net_dir, "IMG_4416_warp_output_net.asp")  # File contenente il predicato posRelNet

    facts_cad = os.path.join(cad_dir, "0A00018253.04_cad.asp")  # File contenente il predicato cad
    output_cad = os.path.join(cad_dir, "0A00018253.04_output_cad.asp")  # File contenente il predicato posRelCad

    ################################################################################################################
    # Rappresentazione grafo delle componenti riconosciute sull'immagine
    fig, ax = get_ax()

    comp_net = parser_component(facts_net)
    neig_net = parser_neighbour(output_net)

    G_net = nx.Graph()

    nodes_net = [i + 1 for i in range(len(comp_net))]
    edge = [(lst[1], lst[3]) for lst in neig_net]

    G_net.add_nodes_from(nodes_net)
    G_net.add_edges_from(edge)

    mapping_net = {}
    for e in comp_net:
        mapping_net[e[1]] = e[0]

    # coordinates for all nodes
    xy = np.zeros([len(comp_net), 2])
    for i, row in enumerate(comp_net):
        xy[i, 0] = (comp_net[i][2] + comp_net[i][4]) / 2
        xy[i, 1] = (comp_net[i][3] + comp_net[i][5]) / 2
    min_max_scaler = preprocessing.MinMaxScaler()
    xy = min_max_scaler.fit_transform(xy)
    for i, row in enumerate(xy):
        xy[i, 1] = 1 - xy[i, 1]

    # position for all nodes
    pos_net = {}
    for i, e in enumerate(comp_net):
        pos_net[e[1]] = xy[i, :]

    edge_labels_net = {}
    for e in neig_net:
        edge_labels_net[e[1], e[3]] = e[4]

    nx.draw_networkx_edge_labels(G_net, pos_net, edge_labels=edge_labels_net, font_color='red')

    # draw the graph
    nx.draw(G_net, pos_net, node_color='skyblue')
    nx.draw_networkx_labels(G_net, pos_net, mapping_net)

    fig.savefig(os.path.join(graph_dir, "graph_net"))
    plt.close(fig)

    ################################################################################################################
    # Rappresentazione grafo delle componenti riconosciute sul CAD
    fig, ax = get_ax()

    comp_cad = parser_component(facts_cad)
    neig_cad = parser_neighbour(output_cad)

    G_cad = nx.Graph()

    nodes_cad = [i + 1 for i in range(len(comp_cad))]
    edge = [(lst[1], lst[3]) for lst in neig_cad]

    G_cad.add_nodes_from(nodes_cad)
    G_cad.add_edges_from(edge)

    mapping_cad = {}
    for e in comp_cad:
        mapping_cad[e[1]] = e[0]

    # coordinates for all nodes
    xy = np.zeros([len(comp_cad), 2])
    for i, row in enumerate(comp_cad):
        xy[i, 0] = (comp_cad[i][2] + comp_cad[i][4]) / 2
        xy[i, 1] = (comp_cad[i][3] + comp_cad[i][5]) / 2
    min_max_scaler = preprocessing.MinMaxScaler()
    xy = min_max_scaler.fit_transform(xy)

    # position for all nodes
    pos_cad = {}
    for i, e in enumerate(comp_cad):
        pos_cad[e[1]] = xy[i, :]

    # draw the graph
    nx.draw(G_cad, pos_cad, node_color='skyblue')
    nx.draw_networkx_labels(G_cad, pos_cad, mapping_cad)

    edge_labels = {}
    for e in neig_cad:
        edge_labels[e[1], e[3]] = e[4]

    nx.draw_networkx_edge_labels(G_cad, pos_cad, edge_labels=edge_labels, font_color='red')

    fig.savefig(os.path.join(graph_dir, "graph_cad"))
    plt.close(fig)

    ################################################################################################################
    # Algoritmo per il match tra i grafi

    th_dist = 0.3
    th_score = 0.8

    green_node = []
    yellow_node = []
    red_node = []

    label_green_edge = []

    max_score = {}

    # ciclo su tutti i nodi del grafo CAD
    for key_cad in mapping_cad:

        # check se esistono nel grafo INF nodi con la stessa label
        keys = [k for k, v in mapping_net.items() if v == mapping_cad[key_cad]]
        if keys:
            for key_net in keys:

                # valuto la distanza euclidea tra il nodo del grafo CAD e il nodo del grafo INF con la stessa label
                dist = np.linalg.norm(pos_cad[key_cad] - pos_net[key_net])
                if dist < th_dist:

                    # definisco delle tuple di relazioni dei nodi per entrambi i grafi
                    # schema @ (label_1, label_2, position)
                    tuple_net = [(tuple_net[0], tuple_net[2], tuple_net[4]) for tuple_net in neig_net if
                                 (mapping_net[key_net] in (tuple_net[0], tuple_net[2]))]
                    tuple_cad = [(tuple_cad[0], tuple_cad[2], tuple_cad[4]) for tuple_cad in neig_cad if
                                 (mapping_cad[key_cad] in (tuple_cad[0], tuple_cad[2]))]

                    # verifico che nei due grafi siano presenti le stesse relazioni tra i nodi
                    count = 0
                    for t_net in tuple_net:
                        if t_net in tuple_cad:
                            label_green_edge += [t_net]
                            count += 1
                    # in base allo score assegno un nodo del grafo INF ad una classe
                    try:
                        score = count / len(tuple_cad)
                        if score > th_score:
                            max_score[key_cad] = (key_net, score)
                            green_node += [key_cad]
                        else:
                            yellow_node += [key_cad]
                    except ZeroDivisionError:
                        print("Il componente {} è isolato".format(mapping_cad[key_cad]))
                else:
                    red_node += [key_cad]
        else:
            red_node += [key_cad]

    green_node = removeDuplicates(green_node)
    yellow_node = removeDuplicates(yellow_node)
    red_node = removeDuplicates(red_node)

    yellow_node, red_node = checkNodeClass(green_node, yellow_node, red_node, max_score)

    ################################################################################################################
    # Definisco la correttezza delle relazioni tra i nodi nel grafo

    # valutazione delle relazioni in base alla label
    label_red_edge = []
    for tpl in neig_cad:
        if (tpl[0], tpl[2], tpl[4]) not in label_green_edge:
            label_red_edge += [(tpl[0], tpl[2], tpl[4])]

    # assegnazione di un colore agli archi del grafo in base all'id dei nodi del grafo CAD
    green_edge = []
    for lst1 in label_green_edge:
        for lst in neig_cad:
            if lst1[0] == lst[0] and lst1[1] == lst[2] and lst1[2] == lst[4]:
                green_edge += [(lst[1], lst[3])]

    red_edge = []
    for lst1 in label_red_edge:
        for lst in neig_cad:
            if lst1[0] == lst[0] and lst1[1] == lst[2] and lst1[2] == lst[4]:
                red_edge += [(lst[1], lst[3])]

    green_edge = removeDuplicates(green_edge)
    red_edge = removeDuplicates(red_edge)

    ################################################################################################################
    # Rappresentazione del grafo CAD colorato in base ai nodi e gli archi riconosciuti

    G_cad_col = nx.Graph()

    G_cad_col.add_nodes_from(nodes_cad)
    edge = [(lst[1], lst[3]) for lst in neig_cad]
    G_cad_col.add_edges_from(edge)

    fig, ax = get_ax()

    # draw the graph
    nx.draw(G_cad_col, pos_cad)

    nx.draw_networkx_nodes(G_cad_col, pos_cad, nodelist=green_node, node_color="lightgreen")
    nx.draw_networkx_nodes(G_cad_col, pos_cad, nodelist=yellow_node, node_color="yellow")
    nx.draw_networkx_nodes(G_cad_col, pos_cad, nodelist=red_node, node_color="red")

    nx.draw_networkx_edges(G_cad_col, pos_cad, edgelist=red_edge, edge_color="red")
    nx.draw_networkx_edges(G_cad_col, pos_cad, edgelist=green_edge, edge_color="green")

    nx.draw_networkx_labels(G_cad_col, pos_cad, mapping_cad)
    # nx.draw_networkx_edge_labels(G_cad_col, pos_cad, edge_labels=edge_labels, font_color='skyblue')

    fig.savefig(os.path.join(graph_dir, "validation_graph"))
    plt.close(fig)


################################################################################################################
# load files

if __name__ == '__main__':
    main()
