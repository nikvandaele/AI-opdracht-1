import json
import csv
from operator import contains

from src.Zoek import Zoekgraaf
from src.Bayes import Bayes
from src.HMM import HMM
import numpy as np


class NHS:
    def __init__(self, pad: str):
        self.pad: str = pad
        self.stad: dict = json.load(open(pad + "/city_graph.json"))
        self.wegKansen: dict = json.load(open(pad + "/road_probabilities.json"))
        self.verkeersKansen: dict = json.load(open(pad + "/traffic_probabilities.json"))
        self.hulpverlenerst: csv.DictReader[str] = csv.DictReader(open(pad + "/responders.csv"))
        self.incidenten: csv.DictReader[str] = csv.DictReader(open(pad + "/incidents.csv"))
        wegMeldingCSV: csv.DictReader[str] = csv.DictReader(open(pad + "/road_reports.csv"))
        verkeersObservatieCSV: csv.DictReader[str] = csv.DictReader(open(pad + "/observed_traffic.csv"))
        self.stadsGraaf: Zoekgraaf = Zoekgraaf(self.stad)
        self.plan: dict = dict()
        self.statistieken: str = ""

        self.wegMeldingen: dict[tuple[str, str], list[dict]] = dict()
        for melding in wegMeldingCSV:
            if not contains(self.wegMeldingen, (melding["from"], melding["to"])):
                self.wegMeldingen[(melding["from"], melding["to"])] = []
            self.wegMeldingen[(melding["from"], melding["to"])].append(melding)

        self.verkeersObservaties: dict[tuple[str, str], dict[int, dict]] = dict()
        for observatie in verkeersObservatieCSV:
            if not contains(self.verkeersObservaties, (observatie["from"], observatie["to"])):
                self.verkeersObservaties[(observatie["from"], observatie["to"])] = dict()
            self.verkeersObservaties[(observatie["from"], observatie["to"])][int(observatie["observation_nr"])] = observatie

    def run(self) -> bool:
        print(self.stadsGraaf.aSter("N2", "N1"))

        wegen: list[tuple[str, str]] = []
        for boog in self.stad["roads"]:
            wegen.append((boog["from"], boog["to"]))

        bayes: Bayes = Bayes(self.wegKansen, self.wegMeldingen, wegen)
        print(bayes.condities)

        print(np.zeros((3, 10)))
        hmm: HMM = HMM(self.verkeersKansen, self.verkeersObservaties)

        return True