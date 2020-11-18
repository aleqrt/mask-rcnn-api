import itertools


class Neighbour:
    """
    NeighbourRelation class implements python class of 'neighbour' atom in DLV rules
    """

    position = {'LEFT': "LEFT", 'RIGHT': "RIGHT", 'TOP': "TOP", 'BOTTOM': "BOTTOM"}

    def __init__(self, component1, id1, component2, id2, position):
        self.component1 = component1
        self.id1 = id1
        self.component2 = component2
        self.id2 = id2
        self.position = position


class Component:
    """
    Component class implements the python class of 'component' atom in DLV rule
    """
    def __init__(self, label, x1, y1, x2, y2, x3, y3, x4, y4):
        self.id = id()
        self.label = label
        self.x1 = x1
        self.x2 = x2
        self.x3 = x3
        self.x4 = x4
        self.y1 = y1
        self.y2 = y2
        self.y3 = y3
        self.y4 = y4
