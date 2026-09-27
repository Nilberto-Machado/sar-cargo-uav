"""Scale the validated FreeCAD binary STL from millimetres to metres."""

from collections import Counter
from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "uav_cargo_manufacturable" / "Aircraft rigid-body assembly (Meshed).stl"
OUTPUT = ROOT / "openfoam" / "manufacturable_vtol" / "constant" / "geometry" / "CargoUAV_manufacturable_m.stl"
SCALE = 0.001


data = SOURCE.read_bytes()
if len(data) < 84:
    raise RuntimeError("STL is too short to be a binary STL")

triangle_count = struct.unpack_from("<I", data, 80)[0]
expected_size = 84 + 50 * triangle_count
if len(data) != expected_size:
    raise RuntimeError(f"Unexpected STL size: {len(data)} bytes, expected {expected_size}")

output = bytearray(data)
output[:80] = b"CargoUAV manufacturable assembly; coordinates in metres".ljust(80, b" ")
edges = Counter()
vertices = {}
bounds_min = [float("inf")] * 3
bounds_max = [-float("inf")] * 3

offset = 84
for _ in range(triangle_count):
    record = list(struct.unpack_from("<12fH", data, offset))
    record[0:3] = [value for value in record[0:3]]
    ids = []
    for start in (3, 6, 9):
        for axis in range(3):
            record[start + axis] *= SCALE
            value = record[start + axis]
            bounds_min[axis] = min(bounds_min[axis], value)
            bounds_max[axis] = max(bounds_max[axis], value)
        key = tuple(round(record[start + axis], 9) for axis in range(3))
        ids.append(vertices.setdefault(key, len(vertices)))
    for a, b in ((ids[0], ids[1]), (ids[1], ids[2]), (ids[2], ids[0])):
        edges[tuple(sorted((a, b)))] += 1
    struct.pack_into("<12fH", output, offset, *record)
    offset += 50

boundary_edges = sum(count == 1 for count in edges.values())
nonmanifold_edges = sum(count > 2 for count in edges.values())
if boundary_edges or nonmanifold_edges:
    raise RuntimeError(
        f"Invalid surface: {boundary_edges} boundary edges, "
        f"{nonmanifold_edges} non-manifold edges"
    )

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_bytes(output)

dimensions = [bounds_max[i] - bounds_min[i] for i in range(3)]
print(f"Input: {SOURCE}")
print(f"Output: {OUTPUT}")
print(f"Triangles: {triangle_count}")
print("Dimensions [m]: " + " x ".join(f"{value:.6f}" for value in dimensions))
print("Closed manifold surface: yes")
