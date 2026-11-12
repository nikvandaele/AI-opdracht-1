from operator import contains
import numpy as np

class HMM:
    def __init__(self, kansen: dict, observaties: dict[tuple[str, str], dict[int, dict]], wegen: list[tuple[str, str]]):
        self.initieel = np.array([kansen["initial"]["Low"], kansen["initial"]["Medium"], kansen["initial"]["High"]])

        self.transitie = np.array([[kansen["transition"]["Low"]["Low"], kansen["transition"]["Low"]["Medium"], kansen["transition"]["Low"]["High"]],
                                   [kansen["transition"]["Medium"]["Low"], kansen["transition"]["Medium"]["Medium"], kansen["transition"]["Medium"]["High"]],
                                   [kansen["transition"]["High"]["Low"], kansen["transition"]["High"]["Medium"], kansen["transition"]["High"]["High"]]])

        self.emissie = np.array([[kansen["emission"]["Low"]["Low"], kansen["emission"]["Low"]["Medium"], kansen["emission"]["Low"]["High"]],
                                 [kansen["emission"]["Medium"]["Low"], kansen["emission"]["Medium"]["Medium"], kansen["emission"]["Medium"]["High"]],
                                 [kansen["emission"]["High"]["Low"], kansen["emission"]["High"]["Medium"], kansen["emission"]["High"]["High"]]])

        self.observaties: dict[tuple[str, str], list[int]] = dict()

        self.wegen: list[tuple[str, str]] = wegen

        for weg in observaties.keys():
            self.observaties[weg] = []
            for i in range(1, max(observaties[weg].keys()) + 1):
                match observaties[weg][i]["traffic_observation"]:
                    case "Low":
                        self.observaties[weg].append(0)
                    case "Medium":
                        self.observaties[weg].append(1)
                    case "High":
                        self.observaties[weg].append(2)

        self.verkeer: dict[tuple[str, str], str] = dict()

        self.vulRaportLozen()
        self.bepaalVerkeer()

    def vulRaportLozen(self) -> None:
        statussen: list[str] = ["Low", "Medium", "High"]
        for weg in self.wegen:
            if not contains(self.observaties.keys(), weg):
                self.verkeer[weg] = statussen[self.initieel.argmax()]

    def bepaalVerkeer(self):
        statussen: list[str] = ["Low", "Medium", "High"]

        for weg in self.observaties.keys():
            berekendeStatussen: list[str] = self.viterbi(self.observaties[weg], statussen)
            self.verkeer[weg] = berekendeStatussen[-1]

    def viterbi(self, observaties: list[int], statussen: list[str]) -> list[str]:
        T: int = len(observaties)
        N: int = len(statussen)

        viterbi_matrix = np.zeros((N, T))
        backpointer = np.zeros((N, T), dtype=int)

        viterbi_matrix[:, 0] = self.initieel * self.emissie[observaties[0]]

        for t in range(1, T):
            for j in range(N):
                toestandsKansen = viterbi_matrix[:, t-1] * self.transitie[:, j] * self.emissie[observaties[t], j]
                viterbi_matrix[j, t] = np.max(toestandsKansen)
                backpointer[j, t] = np.argmax(toestandsKansen)

        besteLaatsteToestand = np.argmax(viterbi_matrix[:, -1])

        bestePad: list[str] = [statussen[besteLaatsteToestand]]
        for t in range(T - 1, 0, -1):
            besteLaatsteToestand = backpointer[besteLaatsteToestand, t]
            bestePad.insert(0, statussen[besteLaatsteToestand])

        return bestePad