"""Measure blade/airframe interference throughout the current tilt motion."""

from pathlib import Path
import FreeCAD as App

ROOT = Path(__file__).resolve().parent
MODEL = ROOT / "uav_cargo_vtail_animation" / "CargoUAV_HybridVTOL_VTail_TiltRotor_Animated.FCStd"
doc = App.openDocument(str(MODEL))
airframe = doc.getObject("Airframe_VTail").Shape

for code in ("FL", "FR", "RL", "RR"):
    pod = doc.getObject("TiltPod_" + code)
    rotor = doc.getObject("Rotor_" + code)
    blades_local = doc.getObject("Rotor_" + code + "_Blades").Shape
    print(f"\n{code}")
    for angle in (0, -15, -30, -45, -60, -75, -90):
        tilt_pl = App.Placement(pod.Placement.Base, App.Rotation(App.Vector(0, 1, 0), angle))
        rotor_pl = App.Placement(rotor.Placement.Base, App.Rotation(App.Vector(0, 0, 1), 90))
        global_pl = tilt_pl.multiply(rotor_pl)
        blades = blades_local.copy()
        blades.Placement = global_pl
        common = airframe.common(blades)
        distance = airframe.distToShape(blades)[0]
        print(f"  tilt={angle:>3} deg  overlap={common.Volume:10.2f} mm3  clearance={distance:8.2f} mm")

App.closeDocument(doc.Name)

