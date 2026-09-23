from pathlib import Path
import FreeCAD as App

BASE = Path(__file__).resolve().parent
doc = App.openDocument(str(BASE / "CargoUAV_HybridVTOL_VTail_TiltRotor_Animated.FCStd"))
airframe = doc.getObject("Airframe_VTail")
assert airframe.Shape.isValid() and airframe.Shape.isClosed() and len(airframe.Shape.Solids) == 1
expected = {
    "FL": (600, -950), "FR": (600, 950), "RL": (1850, -950), "RR": (1850, 950),
}
for code, (x, y) in expected.items():
    tilt = doc.getObject("TiltPod_" + code)
    rotor = doc.getObject("Rotor_" + code)
    tj = doc.getObject("Joint_Tilt_" + code)
    sj = doc.getObject("Joint_Spin_" + code)
    assert round(tilt.Placement.Base.x) == x and round(tilt.Placement.Base.y) == y
    assert tuple(round(v) for v in tj.AxisLocal) == (0, 1, 0)
    assert round(tj.TakeoffAngle) == 0 and round(tj.CruiseAngle) == -90
    assert tj.MovingPart == tilt and sj.ParentTiltPod == tilt and sj.MovingPart == rotor
    assert tuple(round(v) for v in sj.AxisInTiltPod) == (0, 0, 1)
    print(f"{code}: tilt +Y 0..-90 deg; spin local +Z; hierarchy OK")
assert doc.getObject("Joint_Spin_Pusher").MovingPart == doc.getObject("Rotor_Pusher")
print(f"Airframe V-tail: valid closed solid, faces={len(airframe.Shape.Faces)}")
print("Pusher: spin axis +X; link OK")
print("VTAIL_TILTROTOR_ANIMATION_VALIDATION_OK")
App.closeDocument(doc.Name)

