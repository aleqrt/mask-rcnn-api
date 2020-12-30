import os
import re
import sys
import warnings
import argparse
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


def parser_component(facts_dir, facts_name):
    """Parsificatore del file di fatti ASP.
       Return:
           - component, lista contentente [label, id, x1, y1, x2, y2, x3, y3, x4, y4]
    """
    component = []
    with open(os.path.join(facts_dir, facts_name), 'r') as f:
        for i, line in enumerate(f):
            cmp = line.split('(')[1].split(')')[0].split(',')
            component.append([cmp[0].replace('\"', ''), int(cmp[1]),
                              int(cmp[2]), int(cmp[3]),
                              int(cmp[4]), int(cmp[5]),
                              int(cmp[6]), int(cmp[7]),
                              int(cmp[8]), int(cmp[9]),
                              ])
    return component


def parser_neighbour(output_dir, output_name, flag_img=False):
    """Parsificatore del file di output ASP.
       Return:
           - neighbours, lista contenente [label_1, id_1, label_2, id_2, position]
    """
    with open(os.path.join(output_dir, output_name), 'r') as f:
        for i, line in enumerate(f):
            if i >= 2:
                neighbours = [e for e in re.findall('\((.*?)\)', line)]

    tmp = []
    for e in neighbours:
        tmp.append(e.split(','))

    neighbour = []
    for row in tmp:
        for col in row:
            if not flag_img and col == 'left' or col == 'bottom':
                row[0] = row[0].replace('\"', '')
                row[1] = int(row[1])
                row[2] = row[2].replace('\"', '')
                row[3] = int(row[3])
                if col == 'bottom':
                    row[4] = 'top'
                neighbour.append(row)
            if flag_img and col == 'left' or col == 'top':
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

def main(image_name):
    """Main function for graph comparator
    """
    # image_name = '20200921_101722.jpg'

    facts_name = "facts_{}.txt".format(image_name[:-4])
    facts_dir = os.path.join("reasoner", "inferred")

    dlv_output_name = "output_{}.txt".format(image_name[:-4])
    dlv_output_dir = os.path.join("reasoner", "inferred")

    dlv_program_name = 'neighborhood.asp'
    dlv_program_dir = os.path.join("reasoner", "encoding")

    gt_dir = os.path.join("reasoner", "ground truth")
    facts_gt = "facts_GRETA230V.txt"
    output_gt = "output_GRETA230V.txt"

    ################################################################################################################
    # Rappresentazione grafo delle componenti riconosciute sull'immagine

    comp_inf = parser_component(facts_dir, facts_name)
    neig_inf = parser_neighbour(dlv_output_dir, dlv_output_name, flag_img=True)

    G_inf = nx.Graph()

    nodes_inf = [i + 1 for i in range(len(comp_inf))]
    edge = [(lst[1], lst[3]) for lst in neig_inf]

    G_inf.add_nodes_from(nodes_inf)
    G_inf.add_edges_from(edge)

    mapping_inf = {}
    for e in comp_inf:
        mapping_inf[e[1]] = e[0]

    # coordinates for all nodes
    xy = np.zeros([len(comp_inf), 2])
    for i, row in enumerate(comp_inf):
        xy[i, 0] = (comp_inf[i][2] + comp_inf[i][4] + comp_inf[i][6] + comp_inf[i][8]) / 4
        xy[i, 1] = (comp_inf[i][3] + comp_inf[i][5] + comp_inf[i][7] + comp_inf[i][9]) / 4
    min_max_scaler = preprocessing.MinMaxScaler()
    xy = min_max_scaler.fit_transform(xy)
    for i, row in enumerate(xy):
        xy[i, 1] = 1 - xy[i, 1]

    # position for all nodes
    pos_inf = {}
    for i, e in enumerate(comp_inf):
        pos_inf[e[1]] = xy[i, :]

    # draw the graph
    nx.draw(G_inf, pos_inf, node_color='skyblue')
    nx.draw_networkx_labels(G_inf, pos_inf, mapping_inf)
    
    ################################################################################################################
    # Rappresentazione grafo delle componenti riconosciute sul CAD

    comp_gt = parser_component(gt_dir, facts_gt)
    neig_gt = parser_neighbour(gt_dir, output_gt)

    G_gt = nx.Graph()

    nodes_gt = [i + 1 for i in range(len(comp_gt))]
    edge = [(lst[1], lst[3]) for lst in neig_gt]

    G_gt.add_nodes_from(nodes_gt)
    G_gt.add_edges_from(edge)

    mapping_gt = {}
    for e in comp_gt:
        mapping_gt[e[1]] = e[0]

    # coordinates for all nodes
    xy = np.zeros([len(comp_gt), 2])
    for i, row in enumerate(comp_gt):
        xy[i, 0] = (comp_gt[i][2] + comp_gt[i][4] + comp_gt[i][6] + comp_gt[i][8]) / 4
        xy[i, 1] = (comp_gt[i][3] + comp_gt[i][5] + comp_gt[i][7] + comp_gt[i][9]) / 4
    min_max_scaler = preprocessing.MinMaxScaler()
    xy = min_max_scaler.fit_transform(xy)

    # position for all nodes
    pos_gt = {}
    for i, e in enumerate(comp_gt):
        pos_gt[e[1]] = xy[i, :]

    # draw the graph
    nx.draw(G_gt, pos_gt, node_color='skyblue')
    nx.draw_networkx_labels(G_gt, pos_gt, mapping_gt)
    
    ################################################################################################################
    # Algoritmo per il match tra i grafi

    th_dist = 0.3
    th_score = 0.3

    green_node = []
    yellow_node = []
    red_node = []

    label_green_edge = []

    max_score = {}

    # ciclo su tutti i nodi del grafo CAD
    for key_gt in mapping_gt:

        # check se esistono nel grafo INF nodi con la stessa label
        keys = [k for k, v in mapping_inf.items() if v == mapping_gt[key_gt]]
        if keys:
            for key_inf in keys:

                # valuto la distanza euclidea tra il nodo del grafo CAD e il nodo del grafo INF con la stessa label
                dist = np.linalg.norm(pos_gt[key_gt] - pos_inf[key_inf])
                if dist < th_dist:

                    # definisco delle tuple di relazioni dei nodi per entrambi i grafi 
                    # schema @ (label_1, label_2, position)
                    tuple_inf = [(tuple_inf[0], tuple_inf[2], tuple_inf[4]) for tuple_inf in neig_inf if
                                 (mapping_inf[key_inf] in (tuple_inf[0], tuple_inf[2]))]
                    tuple_gt = [(tuple_gt[0], tuple_gt[2], tuple_gt[4]) for tuple_gt in neig_gt if
                                (mapping_gt[key_gt] in (tuple_gt[0], tuple_gt[2]))]

                    # verifico che nei due grafi siano presenti le stesse relazioni tra i nodi
                    count = 0
                    for t_inf in tuple_inf:
                        if t_inf in tuple_gt:
                            label_green_edge.append(t_inf)
                            count += 1

                    # in base allo score assegno un nodo del grafo INF ad una classe
                    score = count / len(tuple_gt)
                    if score > th_score:
                        max_score[key_gt] = (key_inf, score)
                        green_node.append(key_gt)
                    else:
                        yellow_node.append(key_gt)
                else:
                    red_node.append(key_gt)
        else:
            red_node.append(key_gt)

    green_node = removeDuplicates(green_node)
    yellow_node = removeDuplicates(yellow_node)
    red_node = removeDuplicates(red_node)

    yellow_node, red_node = checkNodeClass(green_node, yellow_node, red_node, max_score)
    
    ################################################################################################################
    # Definisco la correttezza delle relazioni tra i nodi nel grafo

    # valutazione delle relazioni in base alla label
    label_red_edge = []
    for tpl in neig_gt:
        if (tpl[0], tpl[2], tpl[4]) not in label_green_edge:
            label_red_edge.append((tpl[0], tpl[2], tpl[4]))

    # assegnazione di un colore agli archi del grafo in base all'id dei nodi del grafo CAD
    green_edge = []
    for lst1 in label_green_edge:
        for lst in neig_gt:
            if lst1[0] == lst[0] and lst1[1] == lst[2] and lst1[2] == lst[4]:
                green_edge.append((lst[1], lst[3]))

    red_edge = []
    for lst1 in label_red_edge:
        for lst in neig_gt:
            if lst1[0] == lst[0] and lst1[1] == lst[2] and lst1[2] == lst[4]:
                red_edge.append((lst[1], lst[3]))

    green_edge = removeDuplicates(green_edge)
    red_edge = removeDuplicates(red_edge)
    
    ################################################################################################################
    # Rappresentazione del grafo CAD colorato in base ai nodi e gli archi riconosciuti

    G_gt_col = nx.Graph()

    G_gt_col.add_nodes_from(nodes_gt)
    edge = [(lst[1], lst[3]) for lst in neig_gt]
    G_gt_col.add_edges_from(edge)

    fig, ax = get_ax()

    # draw the graph
    nx.draw(G_gt_col, pos_gt)

    nx.draw_networkx_nodes(G_gt_col, pos_gt, nodelist=green_node, node_color="lightgreen")
    nx.draw_networkx_nodes(G_gt_col, pos_gt, nodelist=yellow_node, node_color="yellow")
    nx.draw_networkx_nodes(G_gt_col, pos_gt, nodelist=red_node, node_color="red")

    nx.draw_networkx_edges(G_gt_col, pos_gt, edgelist=red_edge, edge_color="red")
    nx.draw_networkx_edges(G_gt_col, pos_gt, edgelist=green_edge, edge_color="green")

    nx.draw_networkx_labels(G_gt_col, pos_gt, mapping_gt)

    fig.savefig(os.path.join("reasoner", "graph", "validation_graph_" + image_name))
    plt.close(fig)
    
################################################################################################################
# load files

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Graph comparator')
    argparser.add_argument('-i', '--image', help='Image name')

    args = argparser.parse_args()

    main(args.image)
