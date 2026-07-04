"""Watch game module for real-time game monitoring and player tracking."""

import urllib.request
import time
import json
import os
import sys

PORT = 8080
URL = f"http://0.0.0.0:{PORT}"


if len(sys.argv) > 1:
    PLAYERS = sys.argv[1:]
else:
    PLAYERS = None

INIT = False
HIST = {}


class SimeisError(Exception):
    """Custom exception for Simeis API errors."""

    pass


NMAX = 30
WIDTH = 100
SCORE = "█"
POTENTIAL = "▒"
VOID = " "

MIN = {}
MAX = {}


def mkbar(score, pot, maxs):
    """Generate a text progress bar for score and potential."""
    if maxs == 0.0:
        ps = 0
        pp = 0
    else:
        ps = score / maxs
        pp = pot / maxs
    nbs = int(WIDTH * ps)
    nbp = int(WIDTH * pp)
    nvoid = WIDTH - nbs - nbp
    return (SCORE * nbs) + (POTENTIAL * nbp) + (VOID * nvoid)


def get(path):
    """Fetch data from the API with reconnection on failure."""
    qry = f"{URL}/{path}"
    while True:
        try:
            with urllib.request.urlopen(qry, timeout=10) as reply:
                data = json.loads(reply.read().decode())
                break
        except Exception as err:
            os.system("clear")
            global INIT, HIST
            HIST = {}
            INIT = False
            print("DEAD SERVER")
            print(err)
            time.sleep(4)
            continue

    err = data.pop("error")
    if err != "ok":
        raise SimeisError(err)

    return data


def get_info():
    """Get current game statistics."""
    return get("gamestats")


def get_resources():
    """Get available resources."""
    return get("resources")


def get_market():
    """Get current market prices."""
    return get("market/prices")


def disp_market(resources):  # pylint: disable=too-many-locals
    """Display formatted market prices."""
    market = get_market()
    max_res_len = max(len(k) for k in market)
    disp = {}
    for res, price in market.items():
        if price is None or price < 0:
            price = 0
        MIN[res] = round(min(MIN[res], price), 2)
        MAX[res] = round(max(MAX[res], price), 2)
        relp = round((price / resources[res]["base-price"]) * 100, 2)
        price = round(price, 3)

        disp[res] = {
            "head": f"{price}",
            "mid": f"({relp} %)",
            "tail": f"({MIN[res]} < {resources[res]['base-price']} < {MAX[res]})",
        }

    max_res = max(len(r) for r in disp)
    max_head = max(len(d["head"]) for d in disp.values())
    max_mid = max(len(d["mid"]) for d in disp.values())
    max_tail = max(len(d["tail"]) for d in disp.values())

    buffer = ""
    for res, d in disp.items():
        res_pad = " " * (max_res + 1 - len(res))
        head_pad = " " * (max_head + 1 - len(d["head"]))
        mid_pad = " " * (max_mid + 1 - len(d["mid"]))
        tail_pad = " " * (max_tail + 1 - len(d["tail"]))
        buffer += f"{res}{res_pad}{d['head']}{head_pad}{d['mid']}{mid_pad}{d['tail']}{tail_pad}\n"

    return buffer


# pylint: disable=too-many-locals
resources = get_resources()
for res, data in resources.items():
    MIN[res] = data["base-price"]
    MAX[res] = data["base-price"]

while True:
    time.sleep(0.5)
    buffer = disp_market(resources)
    buffer += "\n"
    info = get_info()
    with open("scores.json", "w") as f:
        json.dump(info, f)
    if len(info) == 0:
        print("No players on the server")
        continue

    for _, p in info.items():
        if p["lost"]:
            p["score"] = -1.0
            p["potential"] = -1.0

    buffer += f"{len([True for p in info.values() if not p['lost']])} Players still in the game "
    buffer += f"({len([True for p in info.values() if p['lost']])} players lost)\n"
    players = sorted(
        info.items(), key=lambda p: p[1]["score"] + p[1]["potential"], reverse=True
    )[:NMAX]
    max_score = max(max(v["score"], 0) + v["potential"] for v in info.values())
    maxn = max(len(data["name"]) for (_, data) in players)
    for player, data in players:
        if PLAYERS is not None and data["name"] not in PLAYERS:
            continue
        if player not in HIST:
            HIST[player] = []

        spaces = maxn - len(data["name"]) + 1
        if data["lost"]:
            buffer += f"Player {data['name'] + ' ' * spaces} LOST\n"
            continue

        s = max(0, data["score"]) + data["potential"]
        if data["age"] == 0:
            AVG_SCORE = 0.0
        else:
            AVG_SCORE = s / data["age"]
        HIST[player].append((s, AVG_SCORE))
        avg_lasts = max(n[1] for n in HIST[player][-30:])

        progress_bar = mkbar(data["score"], data["potential"], max_score)
        player_info = f"Player {data['name'] + ' ' * spaces} {progress_bar} "
        player_info += f"{round(data['score'], 2)} (~{round(avg_lasts, 2)}/sec)\t"
        player_info += f"potential: {round(data['potential'], 2)}\n"
        buffer += player_info
    os.system("clear")
    print(buffer)
