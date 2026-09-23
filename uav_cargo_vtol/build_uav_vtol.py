"""Generate the consolidated hybrid-VTOL cargo UAV in FreeCAD 1.1+.

All dimensions are millimetres. Edit PARAMS and rerun with FreeCADCmd.
The clean external airframe is exported separately from the five actuator disks.
"""

from pathlib import Path
import math
import FreeCAD as App
import Part
import Mesh

P = {
    "length": 2850.0,
    "span": 4200.0,
    "fuselage_width": 520.0,
    "fuselage_height": 600.0,
    "wing_root_chord": 820.0,
    "wing_tip_chord": 420.0,
    "wing_root_le_x": 820.0,
    "wing_tip_le_x": 980.0,
    "wing_thickness_ratio": 0.12,
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
    "pusher_diameter": 540.0,
    "pusher_plane_x": 2960.0,
    "pusher_disk_thickness": 8.0,
    "vtol_rotor_count": 4,
    "vtol_rotor_diameter": 760.0,
    "vtol_disk_thickness": 6.0,
    "vtol_rotor_plane_z": 220.0,
    "boom_y": 950.0,
    "boom_start_x": 500.0,
    "boom_end_x": 2000.0,
    "boom_radius": 38.0,
    "front_motor_x": 600.0,
    "rear_motor_x": 1850.0,
    "motor_pod_radius": 72.0,
    "motor_pod_height": 180.0,
    "payload_kg": 5.0,
    "range_km": 400.0,
    "mtow_kg": 21.0,
    "cruise_speed_mps": 21.0,
    "vtol_battery_wh": 800.0,
    "starter_generator_w": 750.0,
    "fuel_volume_l": 4.0,
}

BASE = Path(__file__).resolve().parent
OUT = BASE / "exports"
OUT.mkdir(exist_ok=True)


def wire(points):
    pts = [App.Vector(*p) for p in points]
    pts.append(pts[0])
    return Part.makePolygon(pts)


def ellipse(x, width, height, zc=0.0, count=48):
    return wire([
        (x, 0.5 * width * math.cos(2 * math.pi * i / count),
         zc + 0.5 * height * math.sin(2 * math.pi * i / count))
        for i in range(count)
    ])


def naca00(y, chord, xle, zc, thickness, count=24):
    upper, lower = [], []
    for i in range(count + 1):
        beta = math.pi * i / count
        xc = 0.5 * (1 - math.cos(beta))
        yt = 5 * thickness * chord * (
            0.2969 * math.sqrt(max(xc, 0)) - 0.1260 * xc
            - 0.3516 * xc**2 + 0.2843 * xc**3 - 0.1036 * xc**4
        )
        upper.append((xle + xc * chord, y, zc + yt))
        lower.append((xle + xc * chord, y, zc - yt))
    return wire(upper + list(reversed(lower[1:-1])))


def fuselage(p):
    stations = [
        (0, 12, 12, 0), (130, 230, 260, 0), (430, 455, 515, -5),
        (900, p["fuselage_width"], p["fuselage_height"], -15),
        (1500, 500, 570, -10), (2050, 350, 410, 5),
        (2530, 205, 245, 20), (p["length"], 70, 70, 20),
    ]
    return Part.makeLoft([ellipse(*s) for s in stations], True, False)


def wing(p):
    half = p["span"] / 2
    sections = []
    for y in (-half, -280, 280, half):
        f = abs(y) / half
        chord = p["wing_root_chord"] + f * (p["wing_tip_chord"] - p["wing_root_chord"])
        xle = p["wing_root_le_x"] + f * (p["wing_tip_le_x"] - p["wing_root_le_x"])
        zc = 30 + max(abs(y) - 280, 0) * math.tan(math.radians(2))
        sections.append(naca00(y, chord, xle, zc, p["wing_thickness_ratio"]))
    return Part.makeLoft(sections, True, False)


def tailplane(p):
    half = p["tail_span"] / 2
    sections = []
    for y in (-half, -130, 130, half):
        f = abs(y) / half
        chord = p["tail_root_chord"] + f * (p["tail_tip_chord"] - p["tail_root_chord"])
        xle = p["tail_root_le_x"] + f * (p["tail_tip_le_x"] - p["tail_root_le_x"])
        sections.append(naca00(y, chord, xle, 85, p["tail_thickness_ratio"], 18))
    return Part.makeLoft(sections, True, False)


def fin(p):
    z0, z1 = 120, 120 + p["fin_height"]
    xz = [
        (p["fin_root_le_x"], z0),
        (p["fin_root_le_x"] + p["fin_root_chord"], z0),
        (p["fin_tip_le_x"] + p["fin_tip_chord"], z1),
        (p["fin_tip_le_x"], z1),
    ]
    face = Part.Face(wire([(x, -p["fin_thickness"] / 2, z) for x, z in xz]))
    return face.extrude(App.Vector(0, p["fin_thickness"], 0))


def boom_z(p):
    return 30 + max(p["boom_y"] - 280, 0) * math.tan(math.radians(2))


def vtol_structure(p):
    zc = boom_z(p)
    length = p["boom_end_x"] - p["boom_start_x"]
    parts = []
    for y in (-p["boom_y"], p["boom_y"]):
        parts.append(Part.makeCylinder(
            p["boom_radius"], length, App.Vector(p["boom_start_x"], y, zc), App.Vector(1, 0, 0)
        ))
        for x in (p["front_motor_x"], p["rear_motor_x"]):
            parts.append(Part.makeCylinder(
                p["motor_pod_radius"], p["motor_pod_height"],
                App.Vector(x, y, zc - p["motor_pod_height"] / 2), App.Vector(0, 0, 1)
            ))
    result = parts[0]
    for part in parts[1:]:
        result = result.fuse(part)
    return result.removeSplitter()


def pusher_disk(p):
    return Part.makeCylinder(
        p["pusher_diameter"] / 2, p["pusher_disk_thickness"],
        App.Vector(p["pusher_plane_x"] - p["pusher_disk_thickness"] / 2, 0, 20), App.Vector(1, 0, 0)
    )


def vtol_disks(p):
    shapes = []
    z = p["vtol_rotor_plane_z"] - p["vtol_disk_thickness"] / 2
    for y in (-p["boom_y"], p["boom_y"]):
        for x in (p["front_motor_x"], p["rear_motor_x"]):
            shapes.append(Part.makeCylinder(
                p["vtol_rotor_diameter"] / 2, p["vtol_disk_thickness"],
                App.Vector(x, y, z), App.Vector(0, 0, 1)
            ))
    return Part.makeCompound(shapes)


def add_parameters(doc, p):
    obj = doc.addObject("App::FeaturePython", "Parameters")
    obj.Label = "Hybrid VTOL design parameters (edit build_uav_vtol.py to regenerate)"
    lengths = {
        "Length": "length", "WingSpan": "span", "WingRootChord": "wing_root_chord",
        "WingTipChord": "wing_tip_chord", "TailSpan": "tail_span",
        "PusherDiameter": "pusher_diameter", "VTOLRotorDiameter": "vtol_rotor_diameter",
        "VTOLBoomOffset": "boom_y",
    }
    for name, key in lengths.items():
        obj.addProperty("App::PropertyLength", name, "Geometry")
        setattr(obj, name, p[key])
    obj.addProperty("App::PropertyArea", "WingArea", "Geometry")
    obj.WingArea = 0.5 * (p["wing_root_chord"] + p["wing_tip_chord"]) * p["span"]
    obj.addProperty("App::PropertyInteger", "VTOLRotorCount", "Propulsion")
    obj.VTOLRotorCount = p["vtol_rotor_count"]
    for name, value in (
        ("PayloadTarget", f'{p["payload_kg"]:.1f} kg'),
        ("MTOWTarget", f'{p["mtow_kg"]:.1f} kg preliminary'),
        ("RangeTarget", f'{p["range_km"]:.0f} km'),
        ("CruiseSpeed", f'{p["cruise_speed_mps"]:.1f} m/s'),
        ("VTOLBattery", f'12S, {p["vtol_battery_wh"]:.0f} Wh nominal'),
        ("StarterGenerator", f'{p["starter_generator_w"]:.0f} W nominal'),
        ("FuelVolume", f'{p["fuel_volume_l"]:.1f} L preliminary'),
    ):
        obj.addProperty("App::PropertyString", name, "Mission and propulsion")
        setattr(obj, name, value)
    obj.addProperty("App::PropertyString", "CoordinateSystem", "CFD")
    obj.CoordinateSystem = "+X aft, +Y starboard, +Z up; units mm"
    return obj


def add_reference(doc, group, name, label, shape):
    obj = doc.addObject("PartDesign::Feature", name)
    obj.Label = label
    obj.Shape = shape
    obj.addProperty("App::PropertyString", "Usage", "Reference")
    obj.Usage = "Packaging reference only; excluded from CFD exports"
    obj.ViewObject.Visibility = False
    group.addObject(obj)


def stats(shape):
    bb = shape.BoundBox
    return {
        "valid": shape.isValid(), "closed": shape.isClosed(),
        "solids": len(shape.Solids), "faces": len(shape.Faces),
        "volume_mm3": shape.Volume,
        "bbox_mm": (bb.XLength, bb.YLength, bb.ZLength),
    }


doc = App.newDocument("CargoUAV_HybridVTOL_CFD")
add_parameters(doc, P)

airframe_shape = (
    fuselage(P).fuse(wing(P)).fuse(tailplane(P)).fuse(fin(P)).fuse(vtol_structure(P)).removeSplitter()
)
if not airframe_shape.isValid() or not airframe_shape.isClosed() or len(airframe_shape.Solids) != 1:
    raise RuntimeError(f"Invalid airframe result: {stats(airframe_shape)}")

airframe = doc.addObject("PartDesign::Feature", "Airframe")
airframe.Label = "Unified watertight hybrid-VTOL airframe"
airframe.Shape = airframe_shape
airframe.addProperty("App::PropertyString", "CFDUsage", "CFD")
airframe.CFDUsage = "Primary clean external wall: fuselage, wing, tail, booms and four motor pods"

pusher = doc.addObject("PartDesign::Feature", "PusherDisk")
pusher.Label = "Optional 540 mm gasoline pusher actuator disk"
pusher.Shape = pusher_disk(P)
pusher.addProperty("App::PropertyString", "CFDUsage", "CFD")
pusher.CFDUsage = "Separate actuator disk; exclude from clean-airframe runs"

lift = doc.addObject("PartDesign::Feature", "VTOLDisks")
lift.Label = "Four optional 760 mm electric VTOL actuator disks"
lift.Shape = vtol_disks(P)
lift.addProperty("App::PropertyString", "CFDUsage", "CFD")
lift.CFDUsage = "Four separate actuator disks for powered-lift cases"

geometry = doc.addObject("App::DocumentObjectGroup", "Geometry")
for obj in (airframe, pusher, lift):
    geometry.addObject(obj)

layout = doc.addObject("App::DocumentObjectGroup", "ReferenceLayout")
layout.Label = "Internal envelopes not exported"
add_reference(doc, layout, "PayloadEnvelope", "5 kg payload envelope",
              Part.makeBox(700, 400, 320, App.Vector(560, -200, -170)))
add_reference(doc, layout, "VTOLBatteryEnvelope", "12S VTOL battery envelope",
              Part.makeBox(380, 240, 150, App.Vector(1350, -120, -120)))
add_reference(doc, layout, "FuelTankEnvelope", "4 L fuel tank envelope",
              Part.makeCylinder(65, 300, App.Vector(1780, 0, -45), App.Vector(1, 0, 0)))
add_reference(doc, layout, "StarterGeneratorEnvelope", "Starter-generator envelope",
              Part.makeCylinder(65, 130, App.Vector(2540, 0, 20), App.Vector(1, 0, 0)))

doc.recompute()
fcstd = BASE / "CargoUAV_HybridVTOL_CFD.FCStd"
doc.saveAs(str(fcstd))

Part.export([airframe], str(OUT / "CargoUAV_HybridVTOL_airframe.step"))
Part.export([airframe, pusher], str(OUT / "CargoUAV_HybridVTOL_with_pusher.step"))
Part.export([airframe, pusher, lift], str(OUT / "CargoUAV_HybridVTOL_complete.step"))
Mesh.export([airframe], str(OUT / "CargoUAV_HybridVTOL_airframe.stl"), 1.0, 0.15)
Mesh.export([pusher], str(OUT / "CargoUAV_HybridVTOL_pusher_disk.stl"), 1.0, 0.15)
Mesh.export([lift], str(OUT / "CargoUAV_HybridVTOL_vtol_disks.stl"), 1.0, 0.15)

report = (
    "Hybrid VTOL cargo UAV geometry validation\n"
    "=========================================\n"
    f"Airframe: {stats(airframe.Shape)}\n"
    f"Pusher disk: {stats(pusher.Shape)}\n"
    f"VTOL disks: {stats(lift.Shape)}\n"
    f"Wing area: {0.5 * (P['wing_root_chord'] + P['wing_tip_chord']) * P['span'] / 1e6:.3f} m2\n"
    f"Aspect ratio: {P['span']**2 / (0.5 * (P['wing_root_chord'] + P['wing_tip_chord']) * P['span']):.3f}\n"
    f"FreeCAD: {App.Version()}\n"
)
(BASE / "validation_report.txt").write_text(report, encoding="utf-8")
print(f"Saved {fcstd}")
print(report)

