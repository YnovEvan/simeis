"""Property-based testing utilities and example tests."""

import math
import sys
import time
import random


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


def distance():
    """Test distance calculation between random 3D points."""
    x1 = random.randrange(-100, 100)
    y1 = random.randrange(-100, 100)
    z1 = random.randrange(-100, 100)
    a = (x1, y1, z1)

    x2 = random.randrange(-100, 100)
    y2 = random.randrange(-100, 100)
    z2 = random.randrange(-100, 100)
    b = (x2, y2, z2)


create_property_based_test(addition, time_test=3)
create_property_based_test(distance, regressions=[4480881574280375424], time_test=10)
