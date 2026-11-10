import json
import csv
from src.Zoek import Zoekgraaf


class NHS:
    def __init__(self, pad: str):
        self.pad: str = pad
        self.stad: dict = json.load(open(pad + "/city_graph.json"))
        self.wegKansen: dict = json.load(open(pad + "/road_probabilities.json"))
        self.verkeersKansen: dict = json.load(open(pad + "/traffic_probabilities.json"))
        self.hulpverlenerst: csv.DictReader[str] = csv.DictReader(open(pad + "/responders.csv"))
        self.incidenten: csv.DictReader[str] = csv.DictReader(open(pad + "/incidents.csv"))
        wegMeldingCSV: csv.DictReader[str] = csv.DictReader(open(pad + "/road_reports.csv"))
        self.verkeersObservaties: csv.DictReader[str] = csv.DictReader(open(pad + "/observed_traffic.csv"))
        self.stadsGraaf: Zoekgraaf = Zoekgraaf(self.stad)
        self.plan: dict = dict()
        self.statistieken: str = ""

        self.wegMeldingen: dict[tuple[str, str], list[dict]] = dict()
        for melding in wegMeldingCSV:
            self.incidenten[(melding["from"], melding["to"])].append(melding)

    def run(self) -> bool:
        print(self.stadsGraaf.aSter("N19", "N1"))

        for i in self.wegMeldingen:
            print(i)
        return True