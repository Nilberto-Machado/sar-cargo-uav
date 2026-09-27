"""Partition the closed UAV STL into layer-compatible OpenFOAM regions."""

from collections import defaultdict
from pathlib import Path
import math
import struct


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "openfoam" / "manufacturable_vtol" / "constant" / "geometry" / "CargoUAV_manufacturable_m.stl"
OUTPUT = Path(__file__).resolve().parent / "CargoUAV_partitioned_m.stl"

PIVOTS = (
    (0.600, -0.950),
    (0.600, 0.950),
    (2.000, -0.950),
    (2.000, 0.950),
)
ROTOR_Z = 0.053396916 + 0.167


def region_for(centroid):
    x, y, z = centroid
    if x > 2.75 and abs(y) < 0.34 and abs(z) < 0.34:
        return "pusher"
    for pivot_x, pivot_y in PIVOTS:
        dx = x - pivot_x
        dy = y - pivot_y
        if abs(z - ROTOR_Z) < 0.045 and abs(dy) < 0.075 and abs(dx) < 0.40:
            return "rotors"
        if math.hypot(dx, dy) < 0.105 and -0.06 < z < 0.31:
            return "nacelles"
    return "airframe"


data = SOURCE.read_bytes()
triangle_count = struct.unpack_from("<I", data, 80)[0]
if len(data) != 84 + 50 * triangle_count:
    raise RuntimeError("Expected a valid binary STL")

regions = defaultdict(list)
offset = 84
for _ in range(triangle_count):
    values = struct.unpack_from("<12fH", data, offset)
    offset += 50
    normal = values[0:3]
    vertices = (values[3:6], values[6:9], values[9:12])
    centroid = tuple(sum(vertex[axis] for vertex in vertices) / 3 for axis in range(3))
    regions[region_for(centroid)].append((normal, vertices))

with OUTPUT.open("w", encoding="ascii", newline="\n") as stream:
    for name in ("airframe", "nacelles", "rotors", "pusher"):
        stream.write(f"solid {name}\n")
        for normal, vertices in regions[name]:
            stream.write("  facet normal " + " ".join(f"{value:.9g}" for value in normal) + "\n")
            stream.write("    outer loop\n")
            for vertex in vertices:
                stream.write("      vertex " + " ".join(f"{value:.9g}" for value in vertex) + "\n")
            stream.write("    endloop\n  endfacet\n")
        stream.write(f"endsolid {name}\n")

print(f"Input triangles: {triangle_count}")
for name in ("airframe", "nacelles", "rotors", "pusher"):
    print(f"{name}: {len(regions[name])}")
print(f"Output: {OUTPUT}")
