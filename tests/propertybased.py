"""Property-based testing utilities and example tests."""

import argparse
import math
import random
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument(
    "--time",
    type=int,
    default=3,
    help="Durée de test en secondes par propriété (défaut: 3)",
)
args = parser.parse_args()

TIME_TEST = args.time


def create_property_based_test(f, regressions=None, time_test=10):
    """Run a property-based test function with random inputs for a time period."""
    if regressions is None:
        regressions = []
    tstart = time.time()
    i = 0
    while (time.time() - tstart) < time_test:
        if i < len(regressions):
            seed = regressions[i]
        else:
            seed = random.randrange(0, 2**64)
        random.seed(seed)
        try:
            f()
            print("Test", f.__name__, i, "OK")
        except AssertionError as err:
            print("Test", f.__name__, "failed with seed", seed)
            print(err)
            sys.exit(1)
        i += 1


def get_dist(a, b):
    """Calculate Euclidean distance between two 3D points."""
    return math.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2) + ((a[2] - b[2]) ** 2))


def addition():
    """Test addition properties with random values."""
    x = random.randrange(0, 10000)
    y = random.randrange(0, 10000)
    z = random.randrange(0, 10000)

    assert x + y == y + x, f"Commutativité échouée: {x} + {y} != {y} + {x}"
    assert (x + y) + z == x + (y + z), (
        f"Association échouée: ({x}+{y})+{z} != {x}+({y}+{z})"
    )
    assert x + 0 == x, f"Identité échoué: {x} + 0 != {x}"
    assert x + y >= x, f"Somme doit être >= au premier opérateur: {x} + {y} < {x}"
    assert x + y >= y, f"Somme doit être >= au second opérateur: {x} + {y} < {y}"


def rand_point():
    """Génère un point 3D aléatoire."""
    return tuple(random.randrange(-100, 100) for _ in range(3))


def distance():
    """Test distance calculation between random 3D points."""
    a = rand_point()
    b = rand_point()
    c = rand_point()

    dist_ab = get_dist(a, b)
    dist_ac = get_dist(a, c)
    dist_bc = get_dist(b, c)

    assert dist_ab >= 0, f"Distance non-négative échouée: dist(a,b)={dist_ab}"
    assert dist_ab == get_dist(b, a), (
        f"Symétrie échouée: dist(a,b)={dist_ab} != dist(b,a)={get_dist(b, a)}"
    )
    assert get_dist(a, a) == 0, "Distance d'un point à lui-même doit être 0"
    triangle_sum = dist_ab + dist_bc
    assert dist_ac <= triangle_sum + 1e-9, (
        f"Inégalité triangulaire échouée: dist(a,c)={dist_ac} > {triangle_sum}"
    )


create_property_based_test(addition, time_test=TIME_TEST)
create_property_based_test(
    distance,
    regressions=[4480881574280375424],
    time_test=TIME_TEST,
)
