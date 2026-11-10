from operator import contains
import numpy as np

class Bayes:
    def __init__(self, kansen: dict, meldingen: dict[tuple[str, str], list[dict]], wegen: list[tuple[str, str]]):
        self.weerkans = np.array([kansen["weather_prior"]["Clear"], kansen["weather_prior"]["Rain"], kansen["weather_prior"]["Storm"]])
        self.weerGebaseerdeWegStatus: dict = {"Clear" : np.array([kansen["road_status_given_weather"]["Clear"]["Open"], kansen["road_status_given_weather"]["Clear"]["Congested"], kansen["road_status_given_weather"]["Clear"]["Blocked"]]),
                                              "Rain" : np.array([kansen["road_status_given_weather"]["Rain"]["Open"], kansen["road_status_given_weather"]["Rain"]["Congested"], kansen["road_status_given_weather"]["Rain"]["Blocked"]]),
                                              "Storm" : np.array([kansen["road_status_given_weather"]["Storm"]["Open"], kansen["road_status_given_weather"]["Storm"]["Congested"], kansen["road_status_given_weather"]["Storm"]["Blocked"]])}

        self.burgerRapport: dict = {"Open" : np.array([kansen["citizen_report"]["Open"]["Open"], kansen["citizen_report"]["Open"]["Congested"], kansen["citizen_report"]["Open"]["Blocked"]]),
                                    "Congested" : np.array([kansen["citizen_report"]["Congested"]["Open"], kansen["citizen_report"]["Congested"]["Congested"], kansen["citizen_report"]["Congested"]["Blocked"]]),
                                    "Blocked" : np.array([kansen["citizen_report"]["Blocked"]["Open"], kansen["citizen_report"]["Blocked"]["Congested"], kansen["citizen_report"]["Blocked"]["Blocked"]])}

        self.politieRapport: dict = {"Open" : np.array([kansen["police_report"]["Open"]["Open"], kansen["police_report"]["Open"]["Congested"], kansen["police_report"]["Open"]["Blocked"]]),
                                    "Congested" : np.array([kansen["police_report"]["Congested"]["Open"], kansen["police_report"]["Congested"]["Congested"], kansen["police_report"]["Congested"]["Blocked"]]),
                                    "Blocked" : np.array([kansen["police_report"]["Blocked"]["Open"], kansen["police_report"]["Blocked"]["Congested"], kansen["police_report"]["Blocked"]["Blocked"]])}

        self.sensorRapport: dict = {"Open" : np.array([kansen["sensor_report"]["Open"]["Open"], kansen["sensor_report"]["Open"]["Congested"], kansen["sensor_report"]["Open"]["Blocked"]]),
                                    "Congested" : np.array([kansen["sensor_report"]["Congested"]["Open"], kansen["sensor_report"]["Congested"]["Congested"], kansen["sensor_report"]["Congested"]["Blocked"]]),
                                    "Blocked" : np.array([kansen["sensor_report"]["Blocked"]["Open"], kansen["sensor_report"]["Blocked"]["Congested"], kansen["sensor_report"]["Blocked"]["Blocked"]])}

        self.meldingen: dict[tuple[str, str], list[dict]] = meldingen
        self.wegen: list[tuple[str, str]] = wegen
        self.condities: dict[tuple[str, str], str] = dict()

        self.vulRapportLozen()
        self.behandelMeldingen()

    def conditieZonderRapport(self) -> str:
        kansen: list[float] = []
        condities: list[str] = ["Open", "Congested", "Blocked"]
        kansen.append((self.weerkans[0] * self.weerGebaseerdeWegStatus["Clear"][0]) + (self.weerkans[1] * self.weerGebaseerdeWegStatus["Rain"][0]) + (self.weerkans[2] * self.weerGebaseerdeWegStatus["Storm"][0]))
        kansen.append((self.weerkans[0] * self.weerGebaseerdeWegStatus["Clear"][1]) + (self.weerkans[1] * self.weerGebaseerdeWegStatus["Rain"][1]) + (self.weerkans[2] * self.weerGebaseerdeWegStatus["Storm"][1]))
        kansen.append((self.weerkans[0] * self.weerGebaseerdeWegStatus["Clear"][2]) + (self.weerkans[1] * self.weerGebaseerdeWegStatus["Rain"][2]) + (self.weerkans[2] * self.weerGebaseerdeWegStatus["Storm"][2]))

        grootsteKansIndices: list[int] = [0]

        for i in range(3):
            if kansen[i] > kansen[grootsteKansIndices[0]]:
                grootsteKansIndices = [i]
            elif kansen[i] == kansen[grootsteKansIndices[0]]:
                grootsteKansIndices.append(i)

        return condities[min(grootsteKansIndices)]

    def vulRapportLozen(self) -> None:
        conditie: str = self.conditieZonderRapport()

        for weg in self.wegen:
            if not contains(self.meldingen.keys(), weg):
                self.condities[weg] = conditie
        return

    def behandelMeldingen(self) -> None:
        slaOver: list[tuple[str, str]] = []
        condities: list[str] = ["Open", "Congested", "Blocked"]

        for weg in self.meldingen.keys():
            if contains(slaOver, weg):
                continue

            slaOver.append((weg[1], weg[0]))

            verenigdeMeldingen: list[dict] = self.meldingen[weg] + self.meldingen[(weg[1], weg[0])]

            prior = self.weerGebaseerdeWegStatus[verenigdeMeldingen[0]["weather"]]

            product = np.array([1, 1, 1])

            for melding in verenigdeMeldingen:
                match melding["source"]:
                    case "Citizen":
                        product = np.multiply(product, self.burgerRapport[melding["reported_status"]])
                    case "Police":
                        product = np.multiply(product, self.politieRapport[melding["reported_status"]])
                    case "Sensor":
                        product = np.multiply(product, self.sensorRapport[melding["reported_status"]])

            nietGenormaliseerdePosterior = np.multiply(prior, product)

            posterior = nietGenormaliseerdePosterior / np.sum(nietGenormaliseerdePosterior)

            conditie: str = condities[np.argmax(posterior)]

            self.condities[weg] = conditie
            self.condities[(weg[1], weg[0])] = conditie

        return





