"""Simeis SDK for Python - Client library for Simeis game server."""

import json
import math
import os
import string
import sys
import time
import urllib.parse
import urllib.request


class SimeisError(Exception):
    """Custom exception for Simeis API errors."""

    pass


def get_dist(a, b):
    """Calculate Euclidean distance between two 3D points."""
    return math.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2) + ((a[2] - b[2]) ** 2))


def check_has(alld, key, *req):
    """Check if types are present in the list."""
    alltypes = [c[key] for c in alld.values()]
    return all(k in alltypes for k in req)


class SimeisSDK:  # pylint: disable=too-many-public-methods
    """SDK for interacting with the Simeis game server API."""

    def __init__(self, username, ip, port):
        """Initialize the SDK with connection details."""
        self.url = f"http://{ip}:{port}"
        assert self.api("/ping")["ping"] == "pong"
        self.setup_player(username)

    def api(self, path, method="GET", timeout=5, **qry):
        """Make an API request to the server."""
        print(method, path)

        tail = ""
        if len(qry) > 0:
            tail += "?"
            tail += "&".join([f"{k}={urllib.parse.quote(v)}" for k, v in qry.items()])

        qry_url = f"{self.url}{path}{tail}"

        hdr = {}
        if hasattr(self, "player"):
            hdr["Simeis-Key"] = self.player["key"]
        req = urllib.request.Request(qry_url, headers=hdr, method=method)

        with urllib.request.urlopen(req, timeout=timeout) as reply:
            data = json.loads(reply.read().decode())
        err = data.pop("error")
        if err != "ok":
            raise SimeisError(err)

        return data

    def get(self, *args, **kwargs):
        """Perform a GET request."""
        return self.api(*args, method="GET", **kwargs)

    def post(self, *args, **kwargs):
        """Perform a POST request."""
        return self.api(*args, method="POST", **kwargs)

    def setup_player(self, username, force_register=False):
        """Set up player account, creating or loading existing account."""
        username = "".join(
            [c for c in username if c in string.ascii_letters + string.digits]
        ).lower()

        if force_register or not os.path.isfile(f"./{username}.json"):
            player = self.post(f"/player/new/{username}")
            with open(f"./{username}.json", "w") as f:
                json.dump(player, f, indent=2)
            self.player = player
        else:
            with open(f"./{username}.json", "r") as f:
                self.player = json.load(f)

        try:
            player = self.get(f"/player/{self.player['playerId']}")
        except SimeisError:
            return self.setup_player(username, force_register=True)

        if player["money"] <= 0.0:
            print(
                "!!! Player already lost, please restart the server to reset the game"
            )
            sys.exit(0)
        return None

    def get_player_status(self):
        """Get current player status."""
        return self.get("/player/" + str(self.player["playerId"]))

    def get_ship_status(self, ship_id):
        """Get status of a specific ship."""
        return self.get(f"/ship/{ship_id}")

    def get_station_status(self, sta):
        """Get status of a specific station."""
        return self.get(f"/station/{sta}")

    def shop_list_modules(self, sta):
        """List available modules at a station."""
        all_modules = self.get(f"/station/{sta}/shop/modules")
        return all_modules

    def shop_list_ship(self, sta):
        """List available ships at a station."""
        all_ships = self.get(f"/station/{sta}/shipyard/list")["ships"]
        return sorted(all_ships, key=lambda ship: ship["price"])

    def buy_ship(self, sta, shipid):
        """Purchase a ship at a station."""
        return self.post(f"/station/{sta}/shipyard/buy/{shipid}")

    def buy_module_on_ship(self, sta, shipid, modtype):
        """Buy a module for a ship."""
        return self.post(f"/station/{sta}/shop/modules/{shipid}/buy/{modtype}")

    def hire_crew(self, sta, crewtype):
        """Hire a crew member at a station."""
        return self.post(f"/station/{sta}/crew/hire/{crewtype.lower()}")

    def assign_crew_to_ship(self, sta, shipid, operator_id, role):
        """Assign crew member to a ship role."""
        return self.post(
            f"/station/{sta}/crew/assign/{operator_id}/ship/{shipid}/{role}"
        )

    def assign_crew_to_module(self, sta, crew_id, ship_id, mod_id):
        """Assign crew member to a module."""
        return self.post(
            f"/station/{sta}/crew/assign/{crew_id}/ship/{ship_id}/{mod_id}"
        )

    def station_has_trader(self, sta):
        """Check if station has a trader."""
        station = self.get(f"/station/{sta}")
        return check_has(station["crew"], "member_type", "Trader")

    def assign_trader_to_station(self, sta, trader_id):
        """Assign trader to station trading post."""
        return self.post(f"/station/{sta}/crew/assign/{trader_id}/trading")

    def compute_travel_cost(self, ship_id, position):
        """Calculate travel cost for a ship to destination."""
        x, y, z = position
        return self.get(f"/ship/{ship_id}/travelcost/{x}/{y}/{z}")

    def travel(self, ship_id, position, wait_end=True):
        """Navigate ship to position."""
        x, y, z = position
        costs = self.post(f"/ship/{ship_id}/navigate/{x}/{y}/{z}")
        if wait_end:
            time.sleep(costs["duration"])
            self.wait_until_ship_idle(ship_id)

    def wait_until_ship_idle(self, ship_id, ts=1):
        """Wait for ship to become idle."""
        ship = self.get(f"/ship/{ship_id}")
        while ship["state"] != "Idle":
            time.sleep(ts)
            ship = self.get(f"/ship/{ship_id}")

    def buy_hull_for_repair(self, sta, ship_id):
        """Purchase hull for ship repair."""
        ship = self.get(f"/ship/{ship_id}")
        req = int(ship["hull_decay"])
        if req == 0:
            return None

        cargo = self.get(f"/station/{sta}")["cargo"]
        if "Hull" not in cargo["resources"]:
            cargo["resources"]["Hull"] = 0

        if cargo["resources"]["Hull"] < req:
            need = req - cargo["resources"]["Hull"]
            return self.post(f"/market/{sta}/buy/hull/{need}")
        return None

    def repair_ship(self, sta, ship_id):
        """Repair a ship at a station."""
        ship = self.get(f"/ship/{ship_id}")
        req = int(ship["hull_decay"])

        if req == 0:
            return None

        cargo = self.get(f"/station/{sta}")["cargo"]
        if "Hull" not in cargo["resources"]:
            cargo["resources"]["Hull"] = 0

        if cargo["resources"]["Hull"] > 0:
            return self.post(f"/station/{sta}/repair/{ship_id}")

        return None

    def buy_fuel_for_refuel(self, sta, ship_id):
        """Purchase fuel for ship refueling."""
        ship = self.get(f"/ship/{ship_id}")
        req = int(ship["fuel_tank_capacity"] - ship["fuel_tank"])

        if req == 0:
            return None

        cargo = self.get(f"/station/{sta}")["cargo"]
        if "Fuel" not in cargo["resources"]:
            cargo["resources"]["Fuel"] = 0

        if cargo["resources"]["Fuel"] < req:
            need = req - cargo["resources"]["Fuel"]
            return self.post(f"/market/{sta}/buy/fuel/{need}")
        return None

    def refuel_ship(self, sta, ship_id):
        """Refuel a ship at a station."""
        ship = self.get(f"/ship/{ship_id}")
        req = int(ship["fuel_tank_capacity"] - ship["fuel_tank"])

        if req == 0:
            return None

        cargo = self.get(f"/station/{sta}")["cargo"]
        if "Fuel" not in cargo["resources"]:
            cargo["resources"]["Fuel"] = 0

        if cargo["resources"]["Fuel"] > 0:
            return self.post(f"/station/{sta}/refuel/{ship_id}")
        return None

    def scan_planets(self, sta):
        """Scan planets from a station."""
        station = self.get(f"/station/{sta}")
        planets = self.post(f"/station/{sta}/scan")["planets"]
        return sorted(
            planets, key=lambda pla: get_dist(station["position"], pla["position"])
        )

    def start_extraction(self, ship_id):
        """Start resource extraction on a ship."""
        return self.post(f"/ship/{ship_id}/extraction/start")

    def return_station_and_unload_all(self, sta, ship_id):
        """Return ship to station and unload all cargo."""
        ship = self.get(f"/ship/{ship_id}")
        station = self.get(f"/station/{sta}")
        if ship["position"] != station["position"]:
            self.travel(ship["id"], station["position"])
        return self.post(f"/ship/{ship_id}/unload/{sta}/all")

    def get_station_resources(self, sta):
        """Get resources available at a station."""
        return self.get(f"/station/{sta}")["cargo"]["resources"]

    def get_market_prices(self):
        """Get current market prices."""
        return self.get("/market/prices")

    def sell_resource(self, sta, res, amnt):
        """Sell a resource at a station."""
        return self.post(f"/market/{sta}/sell/{res}/{amnt}")

    def buy_resource(self, sta, res, amnt):
        """Buy a resource at a station."""
        return self.post(f"/market/{sta}/buy/{res}/{amnt}")
