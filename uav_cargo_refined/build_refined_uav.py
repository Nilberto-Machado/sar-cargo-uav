"""Build the literature-refined hybrid-VTOL cargo UAV for FreeCAD 1.1+.

All dimensions are millimetres.  The model is a new design candidate and does
not overwrite the accepted manufacturable or animation models.
"""

from pathlib import Path
import json
import math

import FreeCAD as App
import Mesh
import Part


P = {
    "length": 2950.0,
    "span": 4200.0,
    "fuselage_width": 500.0,
    "fuselage_height": 560.0,
    "wing_root_chord": 740.0,
    "wing_tip_chord": 340.0,
    "wing_root_le_x": 840.0,
    "wing_tip_le_x": 970.0,
    "wing_root_thickness_ratio": 0.15,
    "wing_tip_thickness_ratio": 0.12,
    "wing_camber": 0.02,
    "wing_camber_location": 0.40,
    "wing_root_incidence_deg": 2.0,
    "wing_tip_incidence_deg": 0.0,
    "wing_dihedral_deg": 3.0,
    "vtail_half_span": 880.0,
    "vtail_angle_deg": 38.0,
    "vtail_root_chord": 560.0,
    "vtail_tip_chord": 315.0,
    "vtail_root_le_x": 2240.0,
    "vtail_tip_le_x": 2300.0,
    "vtail_thickness_ratio": 0.10,
    "pusher_diameter": 600.0,
    "pusher_plane_x": 3065.0,
    "pusher_disk_thickness": 8.0,
    "vtol_rotor_count": 4,
    "vtol_rotor_diameter": 760.0,
    "vtol_disk_thickness": 6.0,
    "boom_y": 950.0,
    "boom_start_x": 500.0,
    "boom_end_x": 2000.0,
    "boom_radius": 34.0,
    "front_motor_x": 600.0,
    "rear_motor_x": 2000.0,
    "nacelle_length": 320.0,
    "cg_target_x": 1070.0,
    "cg_forward_x": 1010.0,
    "cg_aft_x": 1120.0,
    "payload_kg": 5.0,
    "range_km": 400.0,
    "mtow_kg": 21.0,
    "cruise_speed_mps": 21.0,
}

BASE = Path(__file__).resolve().parent
OUT = BASE / "exports"
OUT.mkdir(parents=True, exist_ok=True)


def closed_wire(points):
    vectors = [App.Vector(*point) for point in points]
    vectors.append(vectors[0])
    return Part.makePolygon(vectors)


def ellipse_wire(x, y_center, z_center, width, height, count=48):
    return closed_wire([
        (
            x,
            y_center + 0.5 * width * math.cos(2.0 * math.pi * i / count),
            z_center + 0.5 * height * math.sin(2.0 * math.pi * i / count),
        )
        for i in range(count)
    ])


def rotate_about_quarter_chord(x, z, xle, chord, zc, incidence_deg):
    angle = math.radians(incidence_deg)
    xq = xle + 0.25 * chord
    dx = x - xq
    dz = z - zc
    return (
        xq + math.cos(angle) * dx + math.sin(angle) * dz,
        zc - math.sin(angle) * dx + math.cos(angle) * dz,
    )


def naca4_wire(y, chord, xle, zc, camber, camber_location, thickness, incidence_deg, count=36):
    upper = []
    lower = []
    for i in range(count + 1):
        beta = math.pi * i / count
        xc = 0.5 * (1.0 - math.cos(beta))
        yt = 5.0 * thickness * (
            0.2969 * math.sqrt(max(xc, 0.0))
            - 0.1260 * xc
            - 0.3516 * xc**2
            + 0.2843 * xc**3
            - 0.1036 * xc**4
        )
        if camber <= 0.0:
            yc = 0.0
            dyc = 0.0
        elif xc < camber_location:
            yc = camber / camber_location**2 * (2.0 * camber_location * xc - xc**2)
            dyc = 2.0 * camber / camber_location**2 * (camber_location - xc)
        else:
            yc = camber / (1.0 - camber_location) ** 2 * (
                (1.0 - 2.0 * camber_location) + 2.0 * camber_location * xc - xc**2
            )
            dyc = 2.0 * camber / (1.0 - camber_location) ** 2 * (camber_location - xc)
        theta = math.atan(dyc)
        xu = xle + chord * (xc - yt * math.sin(theta))
        zu = zc + chord * (yc + yt * math.cos(theta))
        xl = xle + chord * (xc + yt * math.sin(theta))
        zl = zc + chord * (yc - yt * math.cos(theta))
        xu, zu = rotate_about_quarter_chord(xu, zu, xle, chord, zc, incidence_deg)
        xl, zl = rotate_about_quarter_chord(xl, zl, xle, chord, zc, incidence_deg)
        upper.append((xu, y, zu))
        lower.append((xl, y, zl))
    return closed_wire(upper + list(reversed(lower[1:-1])))


def fuselage(p):
    stations = [
        (0.0, 0.0, 0.0, 12.0, 12.0),
        (160.0, 0.0, 5.0, 205.0, 230.0),
        (450.0, 0.0, 0.0, 430.0, 480.0),
        (850.0, 0.0, -10.0, p["fuselage_width"], p["fuselage_height"]),
        (1500.0, 0.0, -10.0, 485.0, 535.0),
        (2050.0, 0.0, 5.0, 330.0, 380.0),
        (2550.0, 0.0, 22.0, 180.0, 215.0),
        (p["length"], 0.0, 25.0, 54.0, 54.0),
    ]
    wires = [ellipse_wire(x, y, z, width, height) for x, y, z, width, height in stations]
    return Part.makeLoft(wires, True, False)


def wing(p):
    half_span = p["span"] / 2.0
    sections = []
    for y in (-half_span, -260.0, 260.0, half_span):
        fraction = abs(y) / half_span
        chord = p["wing_root_chord"] + fraction * (p["wing_tip_chord"] - p["wing_root_chord"])
        xle = p["wing_root_le_x"] + fraction * (p["wing_tip_le_x"] - p["wing_root_le_x"])
        thickness = p["wing_root_thickness_ratio"] + fraction * (
            p["wing_tip_thickness_ratio"] - p["wing_root_thickness_ratio"]
        )
        incidence = p["wing_root_incidence_deg"] + fraction * (
            p["wing_tip_incidence_deg"] - p["wing_root_incidence_deg"]
        )
        zc = 45.0 + max(abs(y) - 260.0, 0.0) * math.tan(math.radians(p["wing_dihedral_deg"]))
        sections.append(naca4_wire(
            y, chord, xle, zc, p["wing_camber"], p["wing_camber_location"],
            thickness, incidence,
        ))
    return Part.makeLoft(sections, True, False)


def symmetric_naca_points(chord, xle, thickness, count=28):
    upper = []
    lower = []
    for i in range(count + 1):
        beta = math.pi * i / count
        xc = 0.5 * (1.0 - math.cos(beta))
        yt = 5.0 * thickness * chord * (
            0.2969 * math.sqrt(max(xc, 0.0))
            - 0.1260 * xc
            - 0.3516 * xc**2
            + 0.2843 * xc**3
            - 0.1036 * xc**4
        )
        upper.append((xle + chord * xc, yt))
        lower.append((xle + chord * xc, -yt))
    return upper + list(reversed(lower[1:-1]))


def vtail_section(sign, distance, p):
    fraction = distance / p["vtail_half_span"]
    chord = p["vtail_root_chord"] + fraction * (p["vtail_tip_chord"] - p["vtail_root_chord"])
    xle = p["vtail_root_le_x"] + fraction * (p["vtail_tip_le_x"] - p["vtail_root_le_x"])
    angle = math.radians(p["vtail_angle_deg"])
    y0 = sign * (75.0 + distance * math.cos(angle))
    z0 = 90.0 + distance * math.sin(angle)
    ny = -sign * math.sin(angle)
    nz = math.cos(angle)
    points = []
    for x, normal_offset in symmetric_naca_points(chord, xle, p["vtail_thickness_ratio"]):
        points.append((x, y0 + ny * normal_offset, z0 + nz * normal_offset))
    return closed_wire(points)


def vtail(p):
    halves = []
    for sign in (-1.0, 1.0):
        sections = [vtail_section(sign, distance, p) for distance in (0.0, 440.0, p["vtail_half_span"])]
        halves.append(Part.makeLoft(sections, True, False))
    return halves[0].fuse(halves[1])


def boom_z(p):
    return 45.0 + max(p["boom_y"] - 260.0, 0.0) * math.tan(math.radians(p["wing_dihedral_deg"]))


def nacelle(pivot_x, y, z, p):
    half = p["nacelle_length"] / 2.0
    stations = [
        (pivot_x - half, 14.0, 14.0),
        (pivot_x - 0.62 * half, 96.0, 112.0),
        (pivot_x, 116.0, 136.0),
        (pivot_x + 0.62 * half, 96.0, 112.0),
        (pivot_x + half, 14.0, 14.0),
    ]
    return Part.makeLoft([ellipse_wire(x, y, z, width, height, 32) for x, width, height in stations], True, False)


def vtol_structure(p):
    z = boom_z(p)
    shapes = []
    boom_length = p["boom_end_x"] - p["boom_start_x"]
    for y in (-p["boom_y"], p["boom_y"]):
        shapes.append(Part.makeCylinder(
            p["boom_radius"], boom_length,
            App.Vector(p["boom_start_x"], y, z), App.Vector(1, 0, 0),
        ))
        for x in (p["front_motor_x"], p["rear_motor_x"]):
            shapes.append(Part.makeCylinder(
                26.0, 150.0, App.Vector(x, y - 75.0, z), App.Vector(0, 1, 0),
            ))
            shapes.append(nacelle(x, y, z, p))
    result = shapes[0]
    for shape in shapes[1:]:
        result = result.fuse(shape)
    return result.removeSplitter()


def pusher_disk(p):
    return Part.makeCylinder(
        p["pusher_diameter"] / 2.0, p["pusher_disk_thickness"],
        App.Vector(p["pusher_plane_x"] - p["pusher_disk_thickness"] / 2.0, 0.0, 25.0),
        App.Vector(1, 0, 0),
    )


def vtol_disks(p):
    z = boom_z(p) + 167.0 - p["vtol_disk_thickness"] / 2.0
    shapes = []
    for y in (-p["boom_y"], p["boom_y"]):
        for x in (p["front_motor_x"], p["rear_motor_x"]):
            shapes.append(Part.makeCylinder(
                p["vtol_rotor_diameter"] / 2.0, p["vtol_disk_thickness"],
                App.Vector(x, y, z), App.Vector(0, 0, 1),
            ))
    return Part.makeCompound(shapes)


def trapezoid_metrics(span, root_chord, tip_chord, root_le, tip_le):
    taper = tip_chord / root_chord
    area = 0.5 * (root_chord + tip_chord) * span
    mac = (2.0 / 3.0) * root_chord * (1.0 + taper + taper**2) / (1.0 + taper)
    y_mac = span / 6.0 * (1.0 + 2.0 * taper) / (1.0 + taper)
    x_le_mac = root_le + (tip_le - root_le) * (2.0 * y_mac / span)
    return {"area": area, "taper": taper, "mac": mac, "y_mac": y_mac, "x_le_mac": x_le_mac}


def design_metrics(p):
    wing_data = trapezoid_metrics(
        p["span"], p["wing_root_chord"], p["wing_tip_chord"],
        p["wing_root_le_x"], p["wing_tip_le_x"],
    )
    tail_span = 2.0 * p["vtail_half_span"]
    tail_data = trapezoid_metrics(
        tail_span, p["vtail_root_chord"], p["vtail_tip_chord"],
        p["vtail_root_le_x"], p["vtail_tip_le_x"],
    )
    wing_ac_x = wing_data["x_le_mac"] + 0.25 * wing_data["mac"]
    tail_ac_x = tail_data["x_le_mac"] + 0.25 * tail_data["mac"]
    tail_arm = tail_ac_x - wing_ac_x
    angle = math.radians(p["vtail_angle_deg"])
    horizontal_equivalent = tail_data["area"] * math.cos(angle) ** 2
    vertical_equivalent = tail_data["area"] * math.sin(angle) ** 2
    rho = 1.225
    weight = p["mtow_kg"] * 9.80665
    area_m2 = wing_data["area"] / 1.0e6
    mac_m = wing_data["mac"] / 1000.0
    return {
        "wing_area_m2": area_m2,
        "wing_aspect_ratio": p["span"] ** 2 / wing_data["area"],
        "wing_taper_ratio": wing_data["taper"],
        "wing_mac_m": mac_m,
        "wing_mac_le_x_m": wing_data["x_le_mac"] / 1000.0,
        "wing_ac_x_m": wing_ac_x / 1000.0,
        "cg_target_percent_mac": 100.0 * (p["cg_target_x"] - wing_data["x_le_mac"]) / wing_data["mac"],
        "wing_loading_n_m2": weight / area_m2,
        "cruise_cl_at_mtow": weight / (0.5 * rho * p["cruise_speed_mps"] ** 2 * area_m2),
        "estimated_stall_speed_mps_clmax_1_3": math.sqrt(2.0 * weight / (rho * area_m2 * 1.3)),
        "root_reynolds_at_cruise": p["cruise_speed_mps"] * p["wing_root_chord"] / 1000.0 / 1.50e-5,
        "tip_reynolds_at_cruise": p["cruise_speed_mps"] * p["wing_tip_chord"] / 1000.0 / 1.50e-5,
        "vtail_true_area_m2": tail_data["area"] / 1.0e6,
        "vtail_aspect_ratio": tail_span**2 / tail_data["area"],
        "vtail_taper_ratio": tail_data["taper"],
        "tail_arm_m": tail_arm / 1000.0,
        "horizontal_tail_equivalent_m2": horizontal_equivalent / 1.0e6,
        "vertical_tail_equivalent_m2": vertical_equivalent / 1.0e6,
        "horizontal_tail_volume": horizontal_equivalent * tail_arm / (wing_data["area"] * wing_data["mac"]),
        "vertical_tail_volume": vertical_equivalent * tail_arm / (wing_data["area"] * p["span"]),
        "total_vtol_disk_area_m2": p["vtol_rotor_count"] * math.pi * (p["vtol_rotor_diameter"] / 2000.0) ** 2,
    }


def shape_stats(shape):
    bounds = shape.BoundBox
    return {
        "valid": bool(shape.isValid()),
        "closed": bool(shape.isClosed()),
        "solids": len(shape.Solids),
        "faces": len(shape.Faces),
        "volume_mm3": shape.Volume,
        "bbox_mm": [bounds.XLength, bounds.YLength, bounds.ZLength],
    }


def add_parameter_object(doc, p, metrics):
    obj = doc.addObject("App::FeaturePython", "DesignParameters")
    obj.Label = "Literature-refined UAV design parameters"
    for name, value in (
        ("Length", p["length"]), ("WingSpan", p["span"]),
        ("WingRootChord", p["wing_root_chord"]), ("WingTipChord", p["wing_tip_chord"]),
        ("VtailHalfSpan", p["vtail_half_span"]), ("PusherDiameter", p["pusher_diameter"]),
        ("CGTargetX", p["cg_target_x"]), ("CGForwardX", p["cg_forward_x"]),
        ("CGAftX", p["cg_aft_x"]),
    ):
        obj.addProperty("App::PropertyLength", name, "Geometry")
        setattr(obj, name, value)
    for name, value in (
        ("WingArea", metrics["wing_area_m2"]),
        ("AspectRatio", metrics["wing_aspect_ratio"]),
        ("TaperRatio", metrics["wing_taper_ratio"]),
        ("HorizontalTailVolume", metrics["horizontal_tail_volume"]),
        ("VerticalTailVolume", metrics["vertical_tail_volume"]),
    ):
        obj.addProperty("App::PropertyFloat", name, "Aerodynamic sizing")
        setattr(obj, name, value)
    for name, value in (
        ("WingAirfoil", "NACA 2415 root blending to NACA 2412 tip"),
        ("WingTwist", "+2 deg root incidence to 0 deg tip: 2 deg washout"),
        ("CGEnvelope", "X = 1.010 to 1.120 m; target 1.070 m; validate by weighing"),
        ("ControlSurfaces", "Ailerons 55-90% semispan; ruddervators 30% chord preliminary"),
        ("Maturity", "Concept candidate: requires new CFD, VLM/6-DOF, structures and mass closure"),
    ):
        obj.addProperty("App::PropertyString", name, "Design basis")
        setattr(obj, name, value)
    return obj


def add_hidden_reference(doc, group, name, label, shape):
    obj = doc.addObject("PartDesign::Feature", name)
    obj.Label = label
    obj.Shape = shape
    obj.addProperty("App::PropertyString", "Usage", "Reference")
    obj.Usage = "Packaging or CG reference only; excluded from CFD exports"
    if App.GuiUp and obj.ViewObject:
        obj.ViewObject.Visibility = False
    group.addObject(obj)
    return obj


metrics = design_metrics(P)
doc = App.newDocument("CargoUAV_Refined_CFD")
add_parameter_object(doc, P, metrics)

components = [fuselage(P), wing(P), vtail(P), vtol_structure(P)]
airframe_shape = components[0]
for component in components[1:]:
    airframe_shape = airframe_shape.fuse(component)
airframe_shape = airframe_shape.removeSplitter()
airframe_stats = shape_stats(airframe_shape)
if not airframe_stats["valid"] or not airframe_stats["closed"] or airframe_stats["solids"] != 1:
    raise RuntimeError(f"Invalid refined airframe: {airframe_stats}")

airframe = doc.addObject("PartDesign::Feature", "AirframeRefined")
airframe.Label = "Unified watertight refined cruise airframe"
airframe.Shape = airframe_shape
airframe.addProperty("App::PropertyString", "CFDUsage", "CFD")
airframe.CFDUsage = "Clean external wall with streamlined cruise nacelles; units mm"

pusher = doc.addObject("PartDesign::Feature", "PusherDisk")
pusher.Label = "Optional 600 mm gasoline pusher actuator disk"
pusher.Shape = pusher_disk(P)
pusher.addProperty("App::PropertyString", "CFDUsage", "CFD")
pusher.CFDUsage = "Separate actuator disk; exclude from clean-airframe runs"

lift = doc.addObject("PartDesign::Feature", "VTOLDisks")
lift.Label = "Four optional 760 mm electric VTOL actuator disks"
lift.Shape = vtol_disks(P)
lift.addProperty("App::PropertyString", "CFDUsage", "CFD")
lift.CFDUsage = "Takeoff reference only; disks are separate from the cruise airframe"

geometry = doc.addObject("App::DocumentObjectGroup", "Geometry")
for item in (airframe, pusher, lift):
    geometry.addObject(item)

references = doc.addObject("App::DocumentObjectGroup", "ReferenceLayout")
references.Label = "Hidden payload, energy and CG envelopes"
add_hidden_reference(doc, references, "PayloadEnvelope", "5 kg payload envelope",
                     Part.makeBox(700, 390, 310, App.Vector(550, -195, -165)))
add_hidden_reference(doc, references, "VTOLBatteryEnvelope", "Forward 12S VTOL battery envelope",
                     Part.makeBox(400, 235, 145, App.Vector(1260, -117.5, -120)))
add_hidden_reference(doc, references, "FuelTankEnvelope", "Fuel tank near target CG",
                     Part.makeCylinder(65, 320, App.Vector(1050, 0, -55), App.Vector(1, 0, 0)))
add_hidden_reference(doc, references, "StarterGeneratorEnvelope", "Aft starter-generator envelope",
                     Part.makeCylinder(65, 130, App.Vector(2600, 0, 25), App.Vector(1, 0, 0)))
add_hidden_reference(doc, references, "CGEnvelope", "Allowable preliminary CG travel",
                     Part.makeCylinder(18, P["cg_aft_x"] - P["cg_forward_x"],
                                       App.Vector(P["cg_forward_x"], 0, 0), App.Vector(1, 0, 0)))

if App.GuiUp:
    airframe.ViewObject.ShapeColor = (0.82, 0.85, 0.88)
    pusher.ViewObject.ShapeColor = (0.25, 0.45, 0.75)
    pusher.ViewObject.Transparency = 70
    lift.ViewObject.ShapeColor = (0.20, 0.65, 0.80)
    lift.ViewObject.Transparency = 78

doc.recompute()
fcstd = BASE / "CargoUAV_Refined_CFD.FCStd"
doc.saveAs(str(fcstd))

Part.export([airframe], str(OUT / "CargoUAV_Refined_airframe.step"))
Part.export([airframe, pusher], str(OUT / "CargoUAV_Refined_with_pusher.step"))
Part.export([airframe, pusher, lift], str(OUT / "CargoUAV_Refined_complete.step"))
Mesh.export([airframe], str(OUT / "CargoUAV_Refined_airframe.stl"), 0.8, 0.12)
Mesh.export([pusher], str(OUT / "CargoUAV_Refined_pusher_disk.stl"), 0.8, 0.12)
Mesh.export([lift], str(OUT / "CargoUAV_Refined_vtol_disks.stl"), 0.8, 0.12)

validation = {
    "freecad_version": list(App.Version()),
    "airframe": airframe_stats,
    "pusher_disk": shape_stats(pusher.Shape),
    "vtol_disks": shape_stats(lift.Shape),
    "parameters": P,
    "metrics": metrics,
}
(BASE / "validation_report.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
print(f"Saved {fcstd}")
print(json.dumps(validation, indent=2))
