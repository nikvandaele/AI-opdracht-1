

class Hulpverlener:
    def __init__(self, info: dict):
        self.id: str = info["responder_id"]
        self.type: str = info["type"]
        self.locatie: str = info["start_location"]
        self.diensten: list[str] = self.leesDiensten(info["capabilities"])
        self.beschikbaar: bool = info["availability"] == "Available"
        self.drukTot: int = int(info["time_until_available"])

    def leesDiensten(self, diensten: str) -> list[str]:
        gelezenDiensten: list[str] = []
        dienst: str = ""

        for ch in diensten:
            if ch == ";":
                gelezenDiensten.append(dienst)
                dienst = ""
                continue
            dienst += ch
        gelezenDiensten.append(dienst)
        return gelezenDiensten