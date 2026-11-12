

class Stats:
    def __init__(self, aantalincidenten: int):
        self.incidenten: int = 0
        self.incidentenPerPrio: list[int] = [0, 0, 0, 0]
        self.hulpverleners: set[str] = set()
        self.responsTijden: list[int] = []
        self.totAantalAncidenten: int = aantalincidenten

    def schrijfWeg(self, pad: str) -> None:
        gemResponsTijd: float = 0
        for i in self.responsTijden:
            gemResponsTijd += i
        gemResponsTijd /= len(self.responsTijden)

        opTijdPrecentage : float = (self.incidenten / self.totAantalAncidenten) * 100

        output : str = f"Statistieken:\n\n{self.incidenten} ({self.incidentenPerPrio[0]} critical, {self.incidentenPerPrio[1]} high, {self.incidentenPerPrio[2]} medium, {self.incidentenPerPrio[3]} low) incidenten afgehandeld door {len(self.hulpverleners)} verschillende hulpverleners.\nMet een gemiddelde responstijd van {round(gemResponsTijd, 1)}s en een op-tijd-percentage van {round(opTijdPrecentage, 1)}%.\n"
        open(pad, "w").write(output)

