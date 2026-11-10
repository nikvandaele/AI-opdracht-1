import math
from operator import contains


class Zoekgraaf:
    def __init__(self, graaf: dict):
        self.knopen: dict[str, dict] = dict()
        self.bogen: dict[tuple[str, str], dict] = dict()

        for knoop in graaf["nodes"]:
            self.knopen[knoop["id"]] = knoop
        for boog in graaf["roads"]:
            self.bogen[(boog["from"], boog["to"])] = boog

    def h(self, knoop1: str, knoop2: str) -> float:
        return self.aftstand((self.knopen[knoop1]["x"], self.knopen[knoop1]["y"]), (self.knopen[knoop2]["x"], self.knopen[knoop2]["y"]))/22.5

    def aftstand(self, knoop1: tuple[int, int], knoop2: tuple[int, int]) -> float:
        return math.sqrt(((knoop1[0] - knoop2[0])**2) + ((knoop1[1] - knoop2[1])**2))

    def getPad(self, van: str, naar: str, ouders: dict[str, str]) -> list[str]:
        pad: list[str] = [naar]
        while pad[-1] != van:
            pad.append(ouders[pad[-1]])
        pad.reverse()
        return pad

    def g(self, van: str, naar: str) -> float:
        kost: float = math.inf
        if contains(self.bogen.keys(), (van, naar)):
            kost = self.bogen[(van, naar)]["distance"]/self.bogen[(van, naar)]["speed"]
        return kost



    def aSter(self, startKnoop: str, doelKnoop: str) -> list[str]:
        openSet: dict[str, float] = dict()
        geslotenSet: dict[str, float] = dict()
        ouders: dict[str, str] = dict()
        gSet: dict[str, float] = dict()

        openSet[startKnoop] = 0
        gSet[startKnoop] = 0

        klaar: bool = False
        while len(openSet) != 0 and not klaar:
            q: str = ""
            laagsteF: float = math.inf
            for knoop in openSet.keys():
                if openSet[knoop] < laagsteF:
                    laagsteF = openSet[knoop]
                    q = knoop

            openSet.pop(q)

            opvolgers: list[str] = []

            for boog in self.bogen.keys():
                if boog[0] == q:
                    opvolgers.append(boog[1])

            for opvolger in opvolgers:
                if opvolger == doelKnoop:
                    ouders[opvolger] = q
                    klaar = True
                    break

                opvolgerG: float = gSet[q] + self.g(q, opvolger)
                opvolgerF: float = self.h(opvolger, doelKnoop) + opvolgerG

                if contains(gSet.keys(), opvolger) and gSet[opvolger] > opvolgerG:
                    gSet[opvolger] = opvolgerG
                elif not contains(gSet.keys(), opvolger):
                    gSet[opvolger] = opvolgerG

                if contains(openSet.keys(), opvolger):
                    if openSet[opvolger] < opvolgerF:
                        continue
                if contains(geslotenSet.keys(), opvolger):
                    if geslotenSet[opvolger] < opvolgerF:
                        continue
                openSet[opvolger] = opvolgerF
                ouders[opvolger] = q

            geslotenSet[q] = laagsteF

        return self.getPad(startKnoop, doelKnoop, ouders)






