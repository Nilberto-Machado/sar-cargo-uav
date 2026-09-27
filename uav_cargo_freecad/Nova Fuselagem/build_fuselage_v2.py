import json
import math
import os

import FreeCAD as App
import Part


STATIONS = [
    # x, center_z, external width, external height (mm)
    (0.0, 0.0, 30.0, 30.0),
    (180.0, 0.0, 220.0, 260.0),
    (450.0, -5.0, 470.0, 540.0),
    (500.0, -10.0, 520.0, 600.0),
    (1300.0, -10.0, 520.0, 600.0),
    (1550.0, -10.0, 490.0, 560.0),
    (2000.0, 5.0, 350.0, 410.0),
    (2350.0, 20.0, 240.0, 300.0),
    (2650.0, 25.0, 150.0, 190.0),
    (2850.0, 25.0, 80.0, 90.0),
]


def analytic_ellipse_wire(x, z_center, width, height):
    center = App.Vector(x, 0.0, z_center)
    # Major axis is vertical; S2 fixes the YZ plane and horizontal radius.
    major = App.Vector(x, 0.0, z_center + 0.5 * height)
    minor_reference = App.Vector(x, 0.5 * width, z_center)
    ellipse = Part.Ellipse(major, minor_reference, center)
    edges = [
        ellipse.toShape(i * 0.5 * math.pi, (i + 1) * 0.5 * math.pi)
        for i in range(4)
    ]
    return Part.Wire(edges)


def bop(shape):
    try:
        shape.check(True)
        return {"passes": True, "error": None}
    except Exception as exc:
        return {"passes": False, "error": str(exc)}


def metrics(shape):
    box = shape.BoundBox
    return {
        "basic_valid": shape.isValid(),
        "bop": bop(shape),
        "shape_type": shape.ShapeType,
        "solids": len(shape.Solids),
        "shells": len(shape.Shells),
        "faces": len(shape.Faces),
        "edges": len(shape.Edges),
        "vertices": len(shape.Vertexes),
        "closed": all(shell.isClosed() for shell in shape.Shells),
        "volume_mm3": shape.Volume,
        "area_mm2": shape.Area,
        "bbox_mm": [box.XMin, box.YMin, box.ZMin, box.XMax, box.YMax, box.ZMax],
    }


def main():
    output_dir = os.environ["CARGO_UAV_FUSELAGE_OUTPUT"]
    os.makedirs(output_dir, exist_ok=True)
    step_path = os.path.join(output_dir, "CargoUAV_fuselage_v2.step")
    fcstd_path = os.path.join(output_dir, "CargoUAV_fuselage_v2.FCStd")
    report_path = os.path.join(output_dir, "CargoUAV_fuselage_v2_report.json")

    wires = [analytic_ellipse_wire(x, zc, width, height) for x, zc, width, height in STATIONS]
    # Ruled interpolation preserves the specified envelope exactly and avoids
    # uncontrolled global-loft overshoot between mission stations.
    fuselage = Part.makeLoft(wires, True, True, False, 1)
    in_memory = metrics(fuselage)
    if not in_memory["bop"]["passes"] or in_memory["solids"] != 1 or not in_memory["closed"]:
        raise RuntimeError("Generated fuselage failed in-memory validation")

    payload = Part.makeBox(700.0, 390.0, 310.0, App.Vector(550.0, -195.0, -165.0))
    contained_volume = fuselage.common(payload).Volume
    payload_ratio = contained_volume / payload.Volume

    doc = App.newDocument("CargoUAV_Fuselage_V2")
    body = doc.addObject("PartDesign::Feature", "Fuselage")
    body.Label = "Mission-compatible analytic-ellipse fuselage"
    body.Shape = fuselage
    reference = doc.addObject("PartDesign::Feature", "PayloadEnvelope")
    reference.Label = "5 kg payload envelope (reference only)"
    reference.Shape = payload
    if reference.ViewObject is not None:
        reference.ViewObject.Visibility = False
    doc.recompute()
    doc.saveAs(fcstd_path)

    fuselage.exportStep(step_path)
    roundtrip = Part.read(step_path)
    after_roundtrip = metrics(roundtrip)
    if not after_roundtrip["bop"]["passes"]:
        raise RuntimeError("STEP failed BOP check after reimport")

    report = {
        "freecad_version": ".".join(App.Version()[:3]),
        "stations_mm": STATIONS,
        "section_bboxes_mm": [
            [w.BoundBox.YMin, w.BoundBox.ZMin, w.BoundBox.YMax, w.BoundBox.ZMax]
            for w in wires
        ],
        "construction": "four analytic elliptical arcs per station; ruled solid loft",
        "payload_envelope_mm": [700.0, 390.0, 310.0],
        "payload_position_mm": [550.0, -195.0, -165.0],
        "payload_containment_percent": 100.0 * payload_ratio,
        "in_memory": in_memory,
        "after_step_roundtrip": after_roundtrip,
        "outputs": {"step": step_path, "fcstd": fcstd_path},
    }
    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    print(json.dumps(report, indent=2))
    App.closeDocument(doc.Name)


if __name__ == "__main__":
    main()
