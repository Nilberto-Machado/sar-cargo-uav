"""Export the latest manufacturable UAV as a clean cruise CFD surface."""

from pathlib import Path
import FreeCAD as App
import Part
import MeshPart


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "uav_cargo_manufacturable" / "CargoUAV_HybridVTOL_Manufacturable.FCStd"
OUT = ROOT / "openfoam" / "cruise_25ms_alpha0" / "constant" / "geometry"
OUT.mkdir(parents=True, exist_ok=True)

doc = App.openDocument(str(SOURCE))
airframe = doc.getObject("Airframe_VTail").Shape.copy()

# The nacelle geometry is stored in pod-local coordinates.  Set the agreed
# cruise angles explicitly instead of depending on a saved animation frame.
for code in ("FL", "FR", "RL", "RR"):
    pod = doc.getObject("TiltPod_" + code)
    nacelle = doc.getObject("Nacelle_" + code).Shape.copy()
    angle = 90.0 if code.startswith("R") else -90.0
    nacelle.Placement = App.Placement(
        pod.Placement.Base,
        App.Rotation(App.Vector(0, 1, 0), angle),
    )
    airframe = airframe.fuse(nacelle)

airframe = airframe.removeSplitter()
if not airframe.isValid():
    raise RuntimeError("The fused cruise airframe is not a valid B-Rep")
if not airframe.isClosed():
    raise RuntimeError("The fused cruise airframe is not closed")
if len(airframe.Solids) != 1:
    raise RuntimeError(f"Expected one fused solid, obtained {len(airframe.Solids)}")

step_path = OUT / "CargoUAV_cruise_mm.step"
Part.export([airframe], str(step_path))

# Tessellate in millimetres, then scale mesh coordinates to metres. STL has no
# unit metadata, so the `_m` suffix is deliberately explicit.
mesh = MeshPart.meshFromShape(
    Shape=airframe,
    LinearDeflection=1.5,
    AngularDeflection=0.20,
    Relative=False,
)
scale = App.Matrix()
scale.A11 = scale.A22 = scale.A33 = 0.001
mesh.transform(scale)
stl_path = OUT / "CargoUAV_cruise_m.stl"
mesh.write(str(stl_path))

b = mesh.BoundBox
print(f"STEP: {step_path}")
print(f"STL:  {stl_path}")
print(f"Facets: {mesh.CountFacets}")
print(
    "Bounds [m]: "
    f"x=({b.XMin:.6f},{b.XMax:.6f}) "
    f"y=({b.YMin:.6f},{b.YMax:.6f}) "
    f"z=({b.ZMin:.6f},{b.ZMax:.6f})"
)
print(f"Closed B-Rep: {airframe.isClosed()}, solids: {len(airframe.Solids)}")

App.closeDocument(doc.Name)
