"""Verify front-forward and rear-aft tilt trajectories against the airframe."""

from pathlib import Path
import FreeCAD as App

ROOT = Path(__file__).resolve().parent
MODEL = ROOT / "uav_cargo_vtail_animation" / "CargoUAV_HybridVTOL_VTail_TiltRotor_Animated.FCStd"
doc = App.openDocument(str(MODEL))
airframe = doc.getObject("Airframe_VTail").Shape

minimum = 1e9
for code in ("FL", "FR", "RL", "RR"):
    pod = doc.getObject("TiltPod_" + code)
    rotor = doc.getObject("Rotor_" + code)
    blades_local = doc.getObject("Rotor_" + code + "_Blades").Shape
    target = -90 if code.startswith("F") else 90
    print(f"\n{code}: target={target:+d} deg")
    for step in range(7):
        angle = target * step / 6
        tilt_pl = App.Placement(pod.Placement.Base, App.Rotation(App.Vector(0, 1, 0), angle))
        rotor_pl = App.Placement(rotor.Placement.Base, App.Rotation(App.Vector(0, 0, 1), 90))
        blades = blades_local.copy()
        blades.Placement = tilt_pl.multiply(rotor_pl)
        overlap = airframe.common(blades).Volume
        clearance = airframe.distToShape(blades)[0]
        minimum = min(minimum, clearance)
        print(f"  tilt={angle:+6.1f}  overlap={overlap:10.2f} mm3  clearance={clearance:8.2f} mm")
        if overlap > 1e-3:
            raise RuntimeError(f"Collision at {code} tilt={angle}")

print(f"\nMIRRORED_TILT_COLLISION_FREE minimum_clearance={minimum:.2f} mm")
App.closeDocument(doc.Name)

