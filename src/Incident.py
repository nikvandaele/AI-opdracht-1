

class Incident:
    def __init__(self, info: dict):
        prioriteitsVertaler: dict[str, int] = {"Low" : 3, "Medium" : 2, "High" : 1, "Critical" : 0}
        self.id: str = info["incident_id"]
        self.locatie: str = info["location"]
        self.prioriteit: int = prioriteitsVertaler[info["priority"]]
        self.deadline: int =  int(info["deadline"])
        self.type: str = info["required_capability"]
        self.tijd: int = int(info["timestamp"])
        self.tijdsduur: int = int(info["time_required"])