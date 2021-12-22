import re
import os
import numpy as np

def flattenList(t):
    return [item for sublist in t for item in sublist]

def getRectangleCenter(coordinates):
    xs1,ys1,xd1,yd1 = coordinates
    return (xd1+xs1)/2,(yd1+ys1)/2

def getDistance(fact1,fact2):
    x1,y1 = getRectangleCenter(fact1)
    x2,y2 = getRectangleCenter(fact2)

    return np.sqrt(((y2-y1)**2)-((x2-x1)**2))

def parseFactFile(file,predicateName):
    facts = []
    for x in file.split("."):
        if f"{predicateName}(" in x and "%" not in x:
            x=x.replace(predicateName,"")
            facts.append(list(eval(x)))
    return facts


def normalizeFacts(facts,k = 10000):
    xmin = np.min([*map(lambda x: x[2],facts)])
    xmax = np.max([*map(lambda x: x[4],facts)])
    ymin = np.min([*map(lambda x: x[3],facts)])
    ymax = np.max([*map(lambda x: x[5],facts)])

    for x in facts:
        x[2] = int(((x[2]-xmin)/(xmax-xmin))*k)
        x[3] = int(((x[3]-ymin)/(ymax-ymin))*k)
        x[4] = int(((x[4]-xmin)/(xmax-xmin))*k)
        x[5] = int(((x[5]-ymin)/(ymax-ymin))*k)

    return facts
#################### MAIN #####################


#netPath = "./facts/IMG_4416_warp_net.asp"
cadPath = "./facts/0A00018253.04_cad.asp"
netPath = "./facts/net1.asp"
#netPath = "./facts/prova_net.asp"
#cadPath = "./facts/prova_cad.asp"

with open(netPath) as f:
    netFile = f.read().replace("\n","")
with open(cadPath) as f:
    cadFile = f.read().replace("\n","")

net = parseFactFile(netFile,"net")
cad = parseFactFile(cadFile,"cad")

net = normalizeFacts(net)
cad = normalizeFacts(cad)

realNet = []
for x in net:
    realNet.append(f"net{tuple(x)}.")

realCad = []
for x in cad:
    realCad.append(f"cad{tuple(x)}.")


with open(f"{os.path.splitext(netPath)[0]}_normalized2.asp","w") as f:
    f.write(' '.join(realNet).replace("'",'"'))

with open(f"{os.path.splitext(cadPath)[0]}_normalized2.asp","w") as f:
    f.write(' '.join(realCad).replace("'",'"'))