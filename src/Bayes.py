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
        self.condities: dict[tuple[str, str], str]

    def conditieZonderRapport(self) -> str:




