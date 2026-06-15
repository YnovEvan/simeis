"""Scénarios de tests pour le SDK Simeis."""

import time

from sdk import SimeisSDK


def scenario1():
    """Scénario: Création d'un joueur et achat d'un vaisseau."""
    print("On créer un nouveau joueur")
    player = SimeisSDK("test1", "localhost", 8080)

    status = player.get_player_status()
    print(status)
    print("Son agent de départ est de 72000.0")
    assert status["money"] == 72000.0
    print("Il n'a aucun vaisseau")
    assert len(status["ships"]) == 0

    ship_id = get_less_expensive_ship(player, status["stations"][0], status["money"])

    print("Quand on achete le vaiseau")
    player.buy_ship(status["stations"][0], ship_id)

    new_status = player.get_player_status()
    print("Alors son argent à diminué")
    assert new_status["money"] < status["money"]
    print("Il a maintenant un vaisseau")
    assert len(new_status["ships"]) == 1

    print(new_status)


def get_less_expensive_ship(player: SimeisSDK, station_id, money):
    """Retourne l'ID du vaisseau le moins cher disponible à la station."""
    market = player.shop_list_ship(station_id)
    print(market)
    for ship in market:
        if ship["price"] <= money:
            return ship["id"]

    raise ValueError("No less expensive ship found")


def scenario2():
    """Scénario: Extraire des ressources et les vendre"""
    print("=== Scénario 2 : Extraction et commerce ===")
    player = SimeisSDK("test2", "localhost", 8080)

    status = player.get_player_status()
    station_id = status["stations"][0]
    initial_money = status["money"]

    print("On achète un premier vaisseau")
    ship_id = get_less_expensive_ship(player, station_id, initial_money)
    player.buy_ship(station_id, ship_id)

    status = player.get_player_status()
    ship = status["ships"][0]["id"]

    print("On embauche un pilote")
    pilot = player.hire_crew(station_id, "Pilot")
    trader = player.hire_crew(station_id, "trader")
    operator = player.hire_crew(station_id, "Operator")
    player.assign_trader_to_station(station_id, trader["id"])
    player.assign_crew_to_ship(station_id, ship, pilot["id"], "pilot")

    planets = player.scan_planets(station_id)
    if planets:
        print(f"Planète cible : {planets[0]}")

        print("On achète un module d'extraction associé à la planète")
        if planets[0]["solid"]:
            player.buy_module_on_ship(station_id, ship, "Miner")
        else:
            player.buy_module_on_ship(station_id, ship, "GasSucker")

        player_status = player.get_player_status()
        print(f"player status: {player_status}")
        player.assign_crew_to_module(
            station_id,
            operator["id"],
            ship,
            "1",
        )

        print("On se déplace vers une planète pour extraire des ressources")
        player.travel(ship, planets[0]["position"])

        print("On commence l'extraction")
        player.start_extraction(ship)

        time.sleep(5)

        print("On retourne à la station et on décharge la cargaison")
        player.return_station_and_unload_all(station_id, ship)

        print("On récupère les ressources disponibles")
        resources = player.get_station_resources(station_id)
        print(f"Ressources à la station : {resources}")
        assert len(resources) > 0, "Aucune ressource trouvée après extraction"

        print("On vend les ressources extraites")
        for resource, amount in resources.items():
            if amount > 0 and resource != "Fuel":
                player.sell_resource(station_id, resource, amount)

        status = player.get_player_status()
        print(f"Argent avant : {initial_money}, Argent après : {status['money']}")
        print("✓ Extraction et vente réussies")
