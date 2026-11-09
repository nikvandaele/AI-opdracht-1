from src.ERS import ERS
import sys

def main(argv: list[str]) -> None:
    if len(sys.argv) < 2:
        print("Niet genoeg argumenten")
        return
    if len(sys.argv) > 2:
        print("te veel argumenten")
        return
    noodSysteem: ERS = ERS(argv[1])
    noodSysteem.run()
    print("solvd")
    return