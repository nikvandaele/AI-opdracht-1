import json
import csv


class NHS:
    def __init__(self, pad: str):
        pad: str = pad
        stad: dict = json.load(open(pad + "/city_graph.json"))
        wegKansen: dict = json.load(open(pad + "/road_probabilities.json"))
        verkeersKansen: dict = json.load(open(pad + "/traffic_probabilities.json"))
        hulpverlenerst: csv.DictReader[str] = csv.DictReader(open(pad + "/responders.csv"))
        incidenten: csv.DictReader[str] = csv.DictReader(open(pad + "/incidents.csv"))
        wegMeldingen: csv.DictReader[str] = csv.DictReader(open(pad + "/road_reports.csv"))
        verkeersObservaties: csv.DictReader[str] = csv.DictReader(open(pad + "/observed_traffic.csv"))
        plan: dict = dict()

    def run(self) -> bool:

        return True