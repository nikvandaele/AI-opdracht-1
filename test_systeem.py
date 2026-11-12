import pytest
import json
import os
import tempfile
import shutil

from src.Zoek import Zoekgraaf
from src.Bayes import Bayes
from src.HMM import HMM
from src.NHS import NHS


@pytest.fixture
def test_graaf_data():
    """Fixture die een eenvoudige testgraaf oplevert."""
    return {
        "nodes": [
            {"id": "A", "x": 0, "y": 0},
            {"id": "B", "x": 100, "y": 0},
            {"id": "C", "x": 100, "y": 100},
            {"id": "D", "x": 200, "y": 0}
        ],
        "roads": [
            {"from": "A", "to": "B", "distance": 100, "speed": 10},  # reistijd: 10s
            {"from": "B", "to": "A", "distance": 100, "speed": 10},
            {"from": "B", "to": "D", "distance": 100, "speed": 10},  # reistijd: 10s
            {"from": "D", "to": "B", "distance": 100, "speed": 10},
            {"from": "A", "to": "C", "distance": 150, "speed": 10},  # reistijd: ~15s
            {"from": "C", "to": "D", "distance": 150, "speed": 10},  # reistijd: ~15s
        ]
    }


# --- 1. TESTS VOOR A* ZOEKALGORITME ---
def test_astar_kortste_pad(test_graaf_data):
    graaf = Zoekgraaf(test_graaf_data)
    pad, tijd = graaf.aSter("A", "D")
    assert pad == ["A", "B", "D"]
    assert tijd == 20


def test_astar_geblokkeerde_weg(test_graaf_data):
    graaf = Zoekgraaf(test_graaf_data)
    graaf.bogen.pop(("B", "D"))  # Blokkeer de directe weg
    pad, tijd = graaf.aSter("A", "D")
    assert pad == ["A", "C", "D"]
    assert tijd == 30


def test_astar_onbereikbaar(test_graaf_data):
    graaf = Zoekgraaf(test_graaf_data)
    graaf.bogen.pop(("B", "D"))
    graaf.bogen.pop(("C", "D"))
    pad, tijd = graaf.aSter("A", "D")
    assert pad == []
    assert tijd == 0


# --- 2. TESTS VOOR BAYESIAN REASONING ---
def test_bayes_wegconditie():
    kansen = {
        "weather_prior": {"Clear": 0.7, "Rain": 0.2, "Storm": 0.1},
        "road_status_given_weather": {
            "Clear": {"Open": 0.9, "Congested": 0.09, "Blocked": 0.01},
            "Rain": {"Open": 0.6, "Congested": 0.3, "Blocked": 0.1},
            "Storm": {"Open": 0.2, "Congested": 0.4, "Blocked": 0.4}
        },
        "citizen_report": {
            "Open": {"Open": 0.8, "Congested": 0.15, "Blocked": 0.05},
            "Congested": {"Open": 0.2, "Congested": 0.7, "Blocked": 0.1},
            "Blocked": {"Open": 0.1, "Congested": 0.2, "Blocked": 0.7}
        },
        "police_report": {
            "Open": {"Open": 0.95, "Congested": 0.04, "Blocked": 0.01},
            "Congested": {"Open": 0.05, "Congested": 0.9, "Blocked": 0.05},
            "Blocked": {"Open": 0.01, "Congested": 0.04, "Blocked": 0.95}
        },
        "sensor_report": {
            "Open": {"Open": 0.9, "Congested": 0.08, "Blocked": 0.02},
            "Congested": {"Open": 0.1, "Congested": 0.8, "Blocked": 0.1},
            "Blocked": {"Open": 0.02, "Congested": 0.08, "Blocked": 0.9}
        }
    }
    meldingen = {
        ("A", "B"): [{"weather": "Storm", "source": "Police", "reported_status": "Blocked"}],
        ("B", "A"): []
    }
    wegen = [("A", "B"), ("B", "A"), ("B", "D")]
    bayes = Bayes(kansen, meldingen, wegen)

    assert bayes.condities[("A", "B")] == "Blocked"
    assert bayes.condities[("B", "D")] == "Open"  # Geen melding -> valt terug op prior


# --- 3. TESTS VOOR HIDDEN MARKOV MODEL ---
def test_hmm_viterbi():
    kansen = {
        "initial": {"Low": 0.6, "Medium": 0.3, "High": 0.1},
        "transition": {
            "Low": {"Low": 0.7, "Medium": 0.2, "High": 0.1},
            "Medium": {"Low": 0.2, "Medium": 0.6, "High": 0.2},
            "High": {"Low": 0.1, "Medium": 0.3, "High": 0.6}
        },
        "emission": {
            "Low": {"Low": 0.8, "Medium": 0.15, "High": 0.05},
            "Medium": {"Low": 0.1, "Medium": 0.8, "High": 0.1},
            "High": {"Low": 0.05, "Medium": 0.15, "High": 0.8}
        }
    }
    observaties = {
        ("A", "B"): {
            1: {"traffic_observation": "Low"},
            2: {"traffic_observation": "Medium"},
            3: {"traffic_observation": "High"}
        }
    }
    wegen = [("A", "B"), ("B", "C")]
    hmm = HMM(kansen, observaties, wegen)
    assert hmm.verkeer[("A", "B")] == "High"
    assert hmm.verkeer[("B", "C")] == "Low"


# --- 4. INTEGRATIE- EN PLANVALIDATIE TEST ---
@pytest.fixture
def temp_scenario_dir():
    """Maakt tijdelijk een complete scenario-map aan voor een volledige NHS-run."""
    test_dir = tempfile.mkdtemp()

    with open(f"{test_dir}/city_graph.json", "w") as f:
        json.dump({
            "nodes": [{"id": "N1", "x": 0, "y": 0}, {"id": "N2", "x": 100, "y": 0}],
            "roads": [{"from": "N1", "to": "N2", "distance": 100, "speed": 10},
                      {"from": "N2", "to": "N1", "distance": 100, "speed": 10}]
        }, f)

    with open(f"{test_dir}/road_probabilities.json", "w") as f:
        json.dump({
            "weather_prior": {"Clear": 1.0, "Rain": 0.0, "Storm": 0.0},
            "road_status_given_weather": {
                "Clear": {"Open": 1.0, "Congested": 0.0, "Blocked": 0.0},
                "Rain": {"Open": 1.0, "Congested": 0.0, "Blocked": 0.0},
                "Storm": {"Open": 1.0, "Congested": 0.0, "Blocked": 0.0}
            },
            "citizen_report": {"Open": {"Open": 1.0, "Congested": 0.0, "Blocked": 0.0},
                               "Congested": {"Open": 0.0, "Congested": 1.0, "Blocked": 0.0},
                               "Blocked": {"Open": 0.0, "Congested": 0.0, "Blocked": 1.0}},
            "police_report": {"Open": {"Open": 1.0, "Congested": 0.0, "Blocked": 0.0},
                              "Congested": {"Open": 0.0, "Congested": 1.0, "Blocked": 0.0},
                              "Blocked": {"Open": 0.0, "Congested": 0.0, "Blocked": 1.0}},
            "sensor_report": {"Open": {"Open": 1.0, "Congested": 0.0, "Blocked": 0.0},
                              "Congested": {"Open": 0.0, "Congested": 1.0, "Blocked": 0.0},
                              "Blocked": {"Open": 0.0, "Congested": 0.0, "Blocked": 1.0}}
        }, f)

    with open(f"{test_dir}/traffic_probabilities.json", "w") as f:
        json.dump({
            "initial": {"Low": 1.0, "Medium": 0.0, "High": 0.0},
            "transition": {"Low": {"Low": 1.0, "Medium": 0.0, "High": 0.0},
                           "Medium": {"Low": 0.0, "Medium": 1.0, "High": 0.0},
                           "High": {"Low": 0.0, "Medium": 0.0, "High": 1.0}},
            "emission": {"Low": {"Low": 1.0, "Medium": 0.0, "High": 0.0},
                         "Medium": {"Low": 0.0, "Medium": 1.0, "High": 0.0},
                         "High": {"Low": 0.0, "Medium": 0.0, "High": 1.0}}
        }, f)

    with open(f"{test_dir}/responders.csv", "w") as f:
        f.write("responder_id,type,start_location,capabilities,availability,time_until_available\n")
        f.write("R1,Ambulance,N1,First aid;CPR,Available,0\n")

    with open(f"{test_dir}/incidents.csv", "w") as f:
        f.write("incident_id,location,priority,deadline,required_capability,timestamp,time_required\n")
        f.write("I1,N2,Critical,50,CPR,5,10\n")

    with open(f"{test_dir}/road_reports.csv", "w") as f:
        f.write("from,to,weather,source,reported_status\n")

    with open(f"{test_dir}/observed_traffic.csv", "w") as f:
        f.write("from,to,observation_nr,traffic_observation\n")

    yield test_dir
    shutil.rmtree(test_dir)


def test_volledige_run_en_validatie(temp_scenario_dir):
    nhs = NHS(temp_scenario_dir)
    nhs.run()

    plan_pad = f"{temp_scenario_dir}/plan.json"
    assert os.path.exists(plan_pad), "plan.json is niet aangemaakt!"

    with open(plan_pad) as f:
        plan = json.load(f)

    assert len(plan) == 1
    taak = plan[0]

    # Validatiechecks op basis van de opdracht-eisen:
    for sleutel in ["responder_id", "incident_id", "path", "time"]:
        assert sleutel in taak

    assert taak["time"] >= 5  # Starttijd mag niet voor de timestamp van het incident liggen
    assert taak["path"][0] == "N1"
    assert taak["path"][-1] == "N2"