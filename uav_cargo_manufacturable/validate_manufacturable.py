"""Validate joints and swept-blade clearance of the manufacturable revision."""

from pathlib import Path
import FreeCAD as App

BASE = Path(__file__).resolve().parent
doc = App.openDocument(str(BASE / "CargoUAV_HybridVTOL_Manufacturable.FCStd"))
airframe = doc.getObject("Airframe_VTail").Shape
assert airframe.isValid() and airframe.isClosed() and len(airframe.Solids) == 1

minimum = 1e9
for code in ("FL", "FR", "RL", "RR"):
    pod = doc.getObject("TiltPod_" + code)
    rotor = doc.getObject("Rotor_" + code)
    blades_local = doc.getObject("Rotor_" + code + "_Blades").Shape
    target = -90 if code.startswith("F") else 90
    expected_x = 600 if code.startswith("F") else 2000
    assert round(pod.Placement.Base.x) == expected_x
    assert round(doc.getObject("Joint_Tilt_" + code).CruiseAngle) == target
    for step in range(19):
        angle = target * step / 18
        tilt_pl = App.Placement(pod.Placement.Base, App.Rotation(App.Vector(0, 1, 0), angle))
        rotor_pl = App.Placement(rotor.Placement.Base, App.Rotation(App.Vector(0, 0, 1), 90))
        blades = blades_local.copy()
        blades.Placement = tilt_pl.multiply(rotor_pl)
        overlap = airframe.common(blades).Volume
        clearance = airframe.distToShape(blades)[0]
        if overlap > 1e-3:
            raise RuntimeError(f"Collision {code} at {angle} deg: {overlap} mm3")
        minimum = min(minimum, clearance)
    print(f"{code}: pivot_x={expected_x} target={target:+d} deg collision-free")

print(f"Minimum sampled blade clearance: {minimum:.2f} mm")
print("MANUFACTURABLE_GEOMETRY_VALIDATION_OK")
App.closeDocument(doc.Name)

