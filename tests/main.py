"""Main launcher for tests in heavy testing"""

from .scenario import scenario1, scenario2, scenario3


def main():
    """Launches the tests"""
    print("Lancement des scénarios")
    scenario1()
    scenario2()
    scenario3()


main()
