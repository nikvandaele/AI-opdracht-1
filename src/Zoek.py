import math

def h(node1: tuple[int, int], node2: tuple[int, int]) -> float:
    return math.sqrt(((node1[0] - node2[0])**2) + ((node1[1] - node2[1])**2))


def Aster():
    return