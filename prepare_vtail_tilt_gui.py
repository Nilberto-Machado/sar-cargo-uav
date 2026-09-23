"""Set GUI visibility/camera for the corrected V-tail tilt-rotor model."""

from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui

ROOT = Path(__file__).resolve().parent
MODEL = ROOT / "uav_cargo_vtail_animation" / "CargoUAV_HybridVTOL_VTail_TiltRotor_Animated.FCStd"
doc = App.openDocument(str(MODEL))

names = ["AircraftAssembly", "Airframe_VTail", "Rotor_Pusher", "Rotor_Pusher_Blades", "GroundPlane", "Marker_CG"]
for code in ("FL", "FR", "RL", "RR"):
    names += ["TiltPod_" + code, "Nacelle_" + code, "Rotor_" + code, "Rotor_" + code + "_Blades", "Marker_Tilt_" + code]
for name in names:
    obj = Gui.activeDocument().getObject(name)
    if obj:
        obj.Visibility = True

Gui.activeDocument().activeView().viewAxonometric()
Gui.activeDocument().activeView().fitAll()
doc.save()
App.closeDocument(doc.Name)
Gui.getMainWindow().close()

