import json
import csv
import math
from operator import contains

from src.Zoek import Zoekgraaf
from src.Bayes import Bayes
from src.HMM import HMM
from src.Hulpverlener import Hulpverlener
from src.Incident import Incident
from src.Stats import Stats


class NHS:
    def __init__(self, pad: str):
        self.pad: str = pad
        self.stad: dict = json.load(open(pad + "/city_graph.json"))
        self.wegKansen: dict = json.load(open(pad + "/road_probabilities.json"))
        self.verkeersKansen: dict = json.load(open(pad + "/traffic_probabilities.json"))
        hulpverlenersCSV: csv.DictReader[str] = csv.DictReader(open(pad + "/responders.csv"))
        incidentenCSV: csv.DictReader[str] = csv.DictReader(open(pad + "/incidents.csv"))
        wegMeldingCSV: csv.DictReader[str] = csv.DictReader(open(pad + "/road_reports.csv"))
        verkeersObservatieCSV: csv.DictReader[str] = csv.DictReader(open(pad + "/observed_traffic.csv"))
        self.stadsGraaf: Zoekgraaf = Zoekgraaf(self.stad)
        self.rampenPlan: list[dict] = []

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

        self.hulpverleners: list[Hulpverlener] = []
        for hulpverlener in hulpverlenersCSV:
            self.hulpverleners.append(Hulpverlener(hulpverlener))

        self.incidenten: list[Incident] = []
        for incident in incidentenCSV:
            self.incidenten.append(Incident(incident))

        self.statistieken: Stats = Stats(len(self.incidenten))

    """
    het eigelijke programma, roept bayes en hmm op en doorloopt dan in een evenementlus de simulatie
    """
    def run(self) -> bool:
        wegen: list[tuple[str, str]] = []
        for boog in self.stad["roads"]:
            wegen.append((boog["from"], boog["to"]))

        bayes: Bayes = Bayes(self.wegKansen, self.wegMeldingen, wegen)
        hmm: HMM = HMM(self.verkeersKansen, self.verkeersObservaties, wegen)

        for weg in hmm.verkeer.keys():
            match hmm.verkeer[weg]:
                case "High":
                    self.stadsGraaf.bogen[weg]["speed"] *= 2/3
                case "Medium":
                    self.stadsGraaf.bogen[weg]["speed"] *= 0.9

        for weg in bayes.condities.keys():
            match bayes.condities[weg]:
                case "Blocked":
                    self.stadsGraaf.bogen.pop(weg, None)
                case "Congested":
                    self.stadsGraaf.bogen[weg]["speed"] *= 2/3

        laatsteDeadline: int = 0
        for incident in self.incidenten:
            if incident.deadline > laatsteDeadline:
                laatsteDeadline = incident.deadline

        teBehandelenIncidenten: list[list[Incident]] = [[], [], [], []]

        for tijd in range(laatsteDeadline + 1):

            # we plaatsen de net beschikbaar geworden incidenten in lijsten die oivereenkomen met hun prioriteitsniveau
            for incident in self.incidenten:
                if incident.tijd == tijd:
                    teBehandelenIncidenten[incident.prioriteit].append(incident)

            teBehandelenIncidenten = self.plan(teBehandelenIncidenten, tijd)

            for hulpverlener in self.hulpverleners:
                if hulpverlener.drukTot <= tijd:
                    hulpverlener.beschikbaar = True

        open(self.pad + "/plan.json", "w").write(json.dumps(self.rampenPlan))
        self.statistieken.schrijfWeg(self.pad + "/statistics.txt")

        return True

    """
    dit is de allocatie functie,
    """
    def plan(self, incidenten: list[list[Incident]], tijd: int) -> list[list[Incident]]:
        overschot: list[list[Incident]] = [[], [], [], []]

        #loopt over de 4 prioriteitsklasses
        for i in range(len(incidenten)):
            beschikbareHulpverleners: list[list[tuple[int, int, list[str]]]] = []

            #loopt over de incidenten in de prioriteitsklasse
            for j in range(len(incidenten[i])):
                beschikbareHulpverleners.append([])                                                                                             #
                for k in range(len(self.hulpverleners)):                                                                                        # we lopen over alle hulpverleners
                    if contains(self.hulpverleners[k].diensten, incidenten[i][j].type) and self.hulpverleners[k].beschikbaar:                   # we checken of de hulverlener het incident kan afhandelen en of die beschikbaar is
                        zoekresultaat: tuple[list[str], int] = self.stadsGraaf.aSter(self.hulpverleners[k].locatie, incidenten[i][j].locatie)   # we vinden het pad
                        aankomstOverschot: int = incidenten[i][j].deadline - (tijd + zoekresultaat[1])                                          # we bepalen hoeveel voor de deadline de hulpverlener zou aankomen
                        if aankomstOverschot >= 0 and len(zoekresultaat[0]) != 0:                                                               # we checken of de hulpverlener er op tijd geraakt en of het pad überhaupt bestaat
                            beschikbareHulpverleners[j].append((k, aankomstOverschot, zoekresultaat[0]))                                        #

            while len(incidenten[i]) != 0:

                # we vinden de broegste deadline
                gekozenIncident: int = 0
                vroegsteDeadline: int = incidenten[i][0].deadline
                for j in range(len(incidenten[i])):
                    if incidenten[i][j].deadline < vroegsteDeadline:
                        vroegsteDeadline = incidenten[i][j].deadline
                        gekozenIncident = j

                # we checken of er überhaupt hulpverlers gevonden zijn die op tij kunnen komen helpen
                if len(beschikbareHulpverleners[gekozenIncident]) != 0:

                    # we kiezen de hulpverlener die er er eerst geraakt
                    gekozenHulpverlener: int = beschikbareHulpverleners[gekozenIncident][0][0]
                    grootsteMarge: int = beschikbareHulpverleners[gekozenIncident][0][1]
                    gekozenPad: list[str] = beschikbareHulpverleners[gekozenIncident][0][2]
                    for j in range(len(beschikbareHulpverleners[gekozenIncident])):
                        if beschikbareHulpverleners[gekozenIncident][j][1] > grootsteMarge:
                            grootsteMarge = beschikbareHulpverleners[gekozenIncident][j][1]
                            gekozenHulpverlener = beschikbareHulpverleners[gekozenIncident][j][0]

                    self.hulpverleners[gekozenHulpverlener].beschikbaar = False
                    self.hulpverleners[gekozenHulpverlener].drukTot = (incidenten[i][gekozenIncident].deadline - grootsteMarge) + incidenten[i][gekozenIncident].tijdsduur
                    self.hulpverleners[gekozenHulpverlener].locatie = incidenten[i][gekozenIncident].locatie

                    self.rampenPlan.append({"responder_id" : self.hulpverleners[gekozenHulpverlener].id, "incident_id" : incidenten[i][gekozenIncident].id,
                                            "path" : gekozenPad, "time" : tijd})
                    self.statistieken.incidenten += 1
                    self.statistieken.incidentenPerPrio[i] += 1
                    self.statistieken.hulpverleners.add(self.hulpverleners[gekozenHulpverlener].id)
                    self.statistieken.responsTijden.append(incidenten[i][gekozenIncident].deadline - grootsteMarge - incidenten[i][gekozenIncident].tijd)

                    incidenten[i].pop(gekozenIncident)
                    beschikbareHulpverleners.pop(gekozenIncident)

                    teVerwijderen: list[tuple[int, tuple[int, int, list[str]]]] = []
                    for j in range(len(beschikbareHulpverleners)):
                        for h in beschikbareHulpverleners[j]:
                            if h[0] == gekozenHulpverlener:
                                teVerwijderen.append((j, h))

                    for v in teVerwijderen:
                        beschikbareHulpverleners[v[0]].remove(v[1])
                else:
                    # we zorgen ervoor dat die incidenten die geen hulpverlener aangewezen konden krijgen volgende tick terug kunnen komen om opnieuw te proberen
                    overschot[i].append(incidenten[i][gekozenIncident])
                    incidenten[i].pop(gekozenIncident)
                    beschikbareHulpverleners.pop(gekozenIncident)

        return overschot
