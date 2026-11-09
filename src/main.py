from src.NHS import NHS
import sys

def main(argv: list[str]) -> None:
    if len(sys.argv) < 2:
        print("Niet genoeg argumenten")
        return
    if len(sys.argv) > 2:
        print("te veel argumenten")
        return
    noodSysteem: NHS = NHS(argv[1])
    noodSysteem.run()
    print("solvd")
    return