"""Find a collision-free rear tilt-pivot X position for aft rotation."""

from pathlib import Path
import FreeCAD as App

ROOT = Path(__file__).resolve().parent
MODEL = ROOT / "uav_cargo_vtail_animation" / "CargoUAV_HybridVTOL_VTail_TiltRotor_Animated.FCStd"
doc = App.openDocument(str(MODEL))
airframe = doc.getObject("Airframe_VTail").Shape
blades_local = doc.getObject("Rotor_RL_Blades").Shape
rotor = doc.getObject("Rotor_RL")
y = -950.0
z = doc.getObject("TiltPod_RL").Placement.Base.z

for x in range(1900, 2301, 50):
    min_clear = 1e9
    max_overlap = 0.0
    for step in range(19):
        angle = 90.0 * step / 18.0
        tilt_pl = App.Placement(App.Vector(x, y, z), App.Rotation(App.Vector(0, 1, 0), angle))
        rotor_pl = App.Placement(rotor.Placement.Base, App.Rotation(App.Vector(0, 0, 1), 90))
        blades = blades_local.copy()
        blades.Placement = tilt_pl.multiply(rotor_pl)
        overlap = airframe.common(blades).Volume
        clearance = airframe.distToShape(blades)[0]
        min_clear = min(min_clear, clearance)
        max_overlap = max(max_overlap, overlap)
    print(f"pivot_x={x} mm  max_overlap={max_overlap:10.2f} mm3  min_clearance={min_clear:7.2f} mm")

App.closeDocument(doc.Name)

