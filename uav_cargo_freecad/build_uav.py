"""Build a parametric cargo UAV for external CFD in FreeCAD 1.1+.

Run with:
  FreeCADCmd build_uav.py

All dimensions are millimetres. Edit PARAMS and run again to regenerate every
deliverable. The saved FCStd also contains the same values as editable custom
properties on the Parameters object.
"""

from pathlib import Path
import math

import FreeCAD as App
import Part
import Mesh


PARAMS = {
    "length": 2850.0,
    "span": 4200.0,
    "fuselage_max_width": 520.0,
    "fuselage_max_height": 600.0,
    "wing_root_chord": 620.0,
    "wing_tip_chord": 340.0,
    "wing_thickness_ratio": 0.12,
    "wing_root_le_x": 920.0,
    "wing_tip_le_x": 1040.0,
    "tail_span": 1350.0,
    "tail_root_chord": 520.0,
    "tail_tip_chord": 300.0,
    "tail_root_le_x": 2180.0,
    "tail_tip_le_x": 2240.0,
    "tail_thickness_ratio": 0.10,
    "fin_height": 620.0,
    "fin_root_chord": 720.0,
    "fin_tip_chord": 300.0,
    "fin_root_le_x": 2010.0,
    "fin_tip_le_x": 2320.0,
    "fin_thickness": 70.0,
    "propeller_diameter": 900.0,
    "propeller_disk_thickness": 8.0,
    "propeller_plane_x": 2960.0,
    "payload_target_kg": 5.0,
    "range_target_km": 400.0,
}

BASE = Path(__file__).resolve().parent
OUT = BASE / "exports"
OUT.mkdir(exist_ok=True)


def polygon_wire(points):
    vectors = [App.Vector(*p) for p in points]
    vectors.append(vectors[0])
    return Part.makePolygon(vectors)


def ellipse_wire(x, width, height, zc=0.0, count=48):
    pts = []
    for i in range(count):
        a = 2.0 * math.pi * i / count
        pts.append((x, 0.5 * width * math.cos(a), zc + 0.5 * height * math.sin(a)))
    return polygon_wire(pts)


def naca_symmetric_wire(y, chord, x_le, zc, thickness_ratio, count=24):
    # Cosine spacing around a NACA 00xx profile; finite trailing edge is closed.
    upper = []
    lower = []
    for i in range(count + 1):
        beta = math.pi * i / count
        xc = 0.5 * (1.0 - math.cos(beta))
        yt = 5.0 * thickness_ratio * chord * (
            0.2969 * math.sqrt(max(xc, 0.0))
            - 0.1260 * xc
            - 0.3516 * xc**2
            + 0.2843 * xc**3
            - 0.1036 * xc**4
        )
        upper.append((x_le + xc * chord, y, zc + yt))
        lower.append((x_le + xc * chord, y, zc - yt))
    pts = upper + list(reversed(lower[1:-1]))
    return polygon_wire(pts)


def make_fuselage(p):
    stations = [
        (0.0, 12.0, 12.0, 0.0),
        (130.0, 230.0, 260.0, 0.0),
        (430.0, 455.0, 515.0, -5.0),
        (900.0, p["fuselage_max_width"], p["fuselage_max_height"], -15.0),
        (1500.0, 500.0, 570.0, -10.0),
        (2050.0, 350.0, 410.0, 5.0),
        (2530.0, 205.0, 245.0, 20.0),
        (p["length"], 70.0, 70.0, 20.0),
    ]
    wires = [ellipse_wire(*s) for s in stations]
    return Part.makeLoft(wires, True, False)


def make_wing(p):
    half = 0.5 * p["span"]
    ys = (-half, -280.0, 280.0, half)
    wires = []
    for y in ys:
        f = abs(y) / half
        chord = p["wing_root_chord"] + f * (p["wing_tip_chord"] - p["wing_root_chord"])
        x_le = p["wing_root_le_x"] + f * (p["wing_tip_le_x"] - p["wing_root_le_x"])
        # 2 deg dihedral outside the fuselage.
        zc = 30.0 + max(abs(y) - 280.0, 0.0) * math.tan(math.radians(2.0))
        wires.append(naca_symmetric_wire(y, chord, x_le, zc, p["wing_thickness_ratio"]))
    return Part.makeLoft(wires, True, False)


def make_tailplane(p):
    half = 0.5 * p["tail_span"]
    ys = (-half, -130.0, 130.0, half)
    wires = []
    for y in ys:
        f = abs(y) / half
        chord = p["tail_root_chord"] + f * (p["tail_tip_chord"] - p["tail_root_chord"])
        x_le = p["tail_root_le_x"] + f * (p["tail_tip_le_x"] - p["tail_root_le_x"])
        wires.append(naca_symmetric_wire(y, chord, x_le, 85.0, p["tail_thickness_ratio"], 18))
    return Part.makeLoft(wires, True, False)


def make_fin(p):
    # A tapered vertical tail extruded symmetrically in Y. The root overlaps the fuselage.
    root_z = 120.0
    tip_z = root_z + p["fin_height"]
    points_xz = [
        (p["fin_root_le_x"], root_z),
        (p["fin_root_le_x"] + p["fin_root_chord"], root_z),
        (p["fin_tip_le_x"] + p["fin_tip_chord"], tip_z),
        (p["fin_tip_le_x"], tip_z),
    ]
    face_pts = [(x, -0.5 * p["fin_thickness"], z) for x, z in points_xz]
    face = Part.Face(polygon_wire(face_pts))
    return face.extrude(App.Vector(0.0, p["fin_thickness"], 0.0))


def make_propeller_disk(p):
    # Cylinder axis is X. This is an optional actuator-disk / rotating-zone marker.
    disk = Part.makeCylinder(
        0.5 * p["propeller_diameter"],
        p["propeller_disk_thickness"],
        App.Vector(p["propeller_plane_x"] - 0.5 * p["propeller_disk_thickness"], 0.0, 20.0),
        App.Vector(1.0, 0.0, 0.0),
    )
    return disk


def add_parameters(doc, p):
    obj = doc.addObject("App::FeaturePython", "Parameters")
    obj.Label = "Design parameters (edit build_uav.py to regenerate)"
    dims = {
        "Length": "length",
        "WingSpan": "span",
        "FuselageMaxWidth": "fuselage_max_width",
        "FuselageMaxHeight": "fuselage_max_height",
        "WingRootChord": "wing_root_chord",
        "WingTipChord": "wing_tip_chord",
        "TailSpan": "tail_span",
        "FinHeight": "fin_height",
        "PropellerDiameter": "propeller_diameter",
    }
    for prop, key in dims.items():
        obj.addProperty("App::PropertyLength", prop, "Geometry")
        setattr(obj, prop, p[key])
    obj.addProperty("App::PropertyMass", "PayloadTarget", "Mission")
    obj.PayloadTarget = p["payload_target_kg"]
    obj.addProperty("App::PropertyLength", "RangeTarget", "Mission")
    obj.RangeTarget = p["range_target_km"] * 1_000_000.0
    obj.addProperty("App::PropertyString", "CoordinateSystem", "CFD")
    obj.CoordinateSystem = "+X aft, +Y starboard, +Z up; units mm"
    obj.addProperty("App::PropertyString", "Regeneration", "CFD")
    obj.Regeneration = "Edit PARAMS in build_uav.py and run FreeCADCmd build_uav.py"
    return obj


def shape_stats(shape):
    bb = shape.BoundBox
    return {
        "valid": bool(shape.isValid()),
        "closed": bool(shape.isClosed()),
        "solids": len(shape.Solids),
        "shells": len(shape.Shells),
        "faces": len(shape.Faces),
        "volume_mm3": shape.Volume,
        "area_mm2": shape.Area,
        "bbox_mm": (bb.XLength, bb.YLength, bb.ZLength),
    }


doc = App.newDocument("CargoUAV_CFD")
params_obj = add_parameters(doc, PARAMS)

fuselage = make_fuselage(PARAMS)
wing = make_wing(PARAMS)
tail = make_tailplane(PARAMS)
fin = make_fin(PARAMS)

# Sequential union produces one clean external solid and removes internal splitters.
airframe_shape = fuselage.fuse(wing).fuse(tail).fuse(fin).removeSplitter()
if not airframe_shape.isValid():
    raise RuntimeError("Airframe Boolean result is invalid")
if len(airframe_shape.Solids) != 1:
    raise RuntimeError(f"Expected one airframe solid, got {len(airframe_shape.Solids)}")

airframe = doc.addObject("PartDesign::Feature", "Airframe")
airframe.Label = "Unified watertight airframe"
airframe.Shape = airframe_shape
airframe.addProperty("App::PropertyString", "CFDUsage", "CFD")
airframe.CFDUsage = "Primary external wall surface; single fused closed solid"

disk = doc.addObject("PartDesign::Feature", "PropellerDisk")
disk.Label = "Optional pusher actuator disk"
disk.Shape = make_propeller_disk(PARAMS)
disk.addProperty("App::PropertyString", "CFDUsage", "CFD")
disk.CFDUsage = "Optional actuator disk or rotating-zone reference; omit for clean-airframe CFD"

group = doc.addObject("App::DocumentObjectGroup", "Geometry")
group.addObject(airframe)
group.addObject(disk)

doc.recompute()
fcstd_path = BASE / "CargoUAV_CFD.FCStd"
doc.recompute()
doc.saveAs(str(fcstd_path))

# Neutral CAD exports. Airframe STEP is intentionally one solid.
Part.export([airframe], str(OUT / "CargoUAV_airframe.step"))
Part.export([airframe, disk], str(OUT / "CargoUAV_with_propeller_disk.step"))

# STL: linear deflection 1.0 mm, angular deflection 0.15 rad.
Mesh.export([airframe], str(OUT / "CargoUAV_airframe.stl"), 1.0, 0.15)
Mesh.export([disk], str(OUT / "CargoUAV_propeller_disk.stl"), 1.0, 0.15)

stats = shape_stats(airframe.Shape)
stats_disk = shape_stats(disk.Shape)
report = BASE / "validation_report.txt"
report.write_text(
    "Cargo UAV geometry validation (FreeCAD)\n"
    + "=======================================\n"
    + "Airframe: " + repr(stats) + "\n"
    + "Propeller disk: " + repr(stats_disk) + "\n"
    + f"FreeCAD: {App.Version()}\n",
    encoding="utf-8",
)

print(f"Saved {fcstd_path}")
print(f"Airframe stats: {stats}")
print(f"Propeller disk stats: {stats_disk}")

