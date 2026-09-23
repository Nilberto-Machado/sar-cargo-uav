from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui

ROOT = Path(__file__).resolve().parent
MODEL = ROOT / "uav_cargo_manufacturable" / "CargoUAV_HybridVTOL_Manufacturable.FCStd"
doc = App.openDocument(str(MODEL))
names = ["AircraftAssembly", "Airframe_VTail", "Rotor_Pusher", "Rotor_Pusher_Blades", "GroundPlane", "Marker_CG"]
for code in ("FL", "FR", "RL", "RR"):
    names += ["TiltPod_" + code, "Nacelle_" + code, "Rotor_" + code, "Rotor_" + code + "_Blades", "Marker_Tilt_" + code]
for name in names:
    view = Gui.activeDocument().getObject(name)
    if view:
        view.Visibility = True
Gui.activeDocument().activeView().viewAxonometric()
Gui.activeDocument().activeView().fitAll()
doc.save()
App.closeDocument(doc.Name)
Gui.getMainWindow().close()

