"""Open the animated model in FreeCAD GUI, force visibility and save a diagnostic image."""

from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui

ROOT = Path(__file__).resolve().parent
MODEL = ROOT / "uav_cargo_animation" / "CargoUAV_HybridVTOL_Animated.FCStd"
IMAGE = ROOT / "uav_cargo_animation_preview.png"

doc = App.openDocument(str(MODEL))
Gui.activeDocument().activeView().setAnimationEnabled(False)

visible = (
    "AircraftAssembly", "Airframe",
    "Rotor_VTOL_FL", "Rotor_VTOL_FR", "Rotor_VTOL_RL", "Rotor_VTOL_RR", "Rotor_Pusher",
    "Rotor_VTOL_FL_Blades", "Rotor_VTOL_FR_Blades", "Rotor_VTOL_RL_Blades",
    "Rotor_VTOL_RR_Blades", "Rotor_Pusher_Blades",
    "Marker_Rotor_VTOL_FL", "Marker_Rotor_VTOL_FR", "Marker_Rotor_VTOL_RL",
    "Marker_Rotor_VTOL_RR", "Marker_Rotor_Pusher", "Marker_CG",
    "GroundPlane", "FlightPath",
)

for name in visible:
    view = Gui.activeDocument().getObject(name)
    if view is not None:
        view.Visibility = True

for name in ("KinematicJoints", "RotationMarkers", "AnimationState"):
    view = Gui.activeDocument().getObject(name)
    if view is not None:
        view.Visibility = False

Gui.activeDocument().activeView().viewAxonometric()
Gui.activeDocument().activeView().fitAll()
Gui.activeDocument().activeView().saveImage(str(IMAGE), 1600, 1000, "White")
doc.save()
print(f"Saved diagnostic image: {IMAGE}")
Gui.doCommand("")
App.closeDocument(doc.Name)
Gui.getMainWindow().close()

