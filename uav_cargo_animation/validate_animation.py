"""Structural verification for the animated FreeCAD assembly."""

from pathlib import Path
import FreeCAD as App

BASE = Path(__file__).resolve().parent
doc = App.openDocument(str(BASE / "CargoUAV_HybridVTOL_Animated.FCStd"))

airframe = doc.getObject("Airframe")
assert airframe.Shape.isValid() and airframe.Shape.isClosed() and len(airframe.Shape.Solids) == 1

expected = {
    "Rotor_VTOL_FL": ((600, -950, 220), (0, 0, 1)),
    "Rotor_VTOL_FR": ((600, 950, 220), (0, 0, 1)),
    "Rotor_VTOL_RL": ((1850, -950, 220), (0, 0, 1)),
    "Rotor_VTOL_RR": ((1850, 950, 220), (0, 0, 1)),
    "Rotor_Pusher": ((2960, 0, 20), (1, 0, 0)),
}

for name, (pivot, axis) in expected.items():
    rotor = doc.getObject(name)
    blade = doc.getObject(name + "_Blades")
    joint = doc.getObject("Joint_" + name)
    assert rotor is not None and blade is not None and joint is not None
    assert tuple(round(v, 6) for v in rotor.Placement.Base) == pivot
    assert tuple(round(v, 6) for v in joint.PivotLocal) == pivot
    assert tuple(round(v, 6) for v in joint.RotationAxisLocal) == axis
    assert joint.ParentBody == doc.getObject("AircraftAssembly")
    assert joint.MovingPart == rotor
    assert not blade.Shape.isNull() and blade.Shape.isValid()
    print(f"{name}: pivot={pivot} axis={axis} link=OK shape=OK")

cg_joint = doc.getObject("Joint_AircraftCG")
assert tuple(round(v, 6) for v in cg_joint.CGLocal) == (1350, 0, 0)
assert tuple(round(v, 6) for v in cg_joint.PitchAxisLocal) == (0, 1, 0)
assert cg_joint.MovingBody == doc.getObject("AircraftAssembly")

state = doc.getObject("AnimationState")
for prop in ("SimulationTime", "Phase", "Altitude", "Pitch", "VTOL_RPM", "Pusher_RPM", "AnimationSpeed", "Loop"):
    assert prop in state.PropertiesList

print("Airframe: one valid closed solid")
print("CG: pivot=(1350, 0, 0) axis=(0, 1, 0) link=OK")
print("Animation state and controls: OK")
print("HYBRID_VTOL_ANIMATION_VALIDATION_OK")
App.closeDocument(doc.Name)

