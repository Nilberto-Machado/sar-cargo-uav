"""Independent reopen checks for the generated FreeCAD, STEP and STL files."""

from pathlib import Path
import FreeCAD as App
import Part
import Mesh

BASE = Path(__file__).resolve().parent


def assert_shape(name, shape, expected_solids=1):
    if not shape.isValid():
        raise RuntimeError(f"{name}: invalid BRep")
    if not shape.isClosed():
        raise RuntimeError(f"{name}: BRep is not closed")
    if len(shape.Solids) != expected_solids:
        raise RuntimeError(f"{name}: expected {expected_solids} solid(s), got {len(shape.Solids)}")
    print(
        f"{name}: valid=True closed=True solids={len(shape.Solids)} "
        f"faces={len(shape.Faces)} bbox_mm="
        f"({shape.BoundBox.XLength:.3f}, {shape.BoundBox.YLength:.3f}, {shape.BoundBox.ZLength:.3f})"
    )


doc = App.openDocument(str(BASE / "CargoUAV_CFD.FCStd"))
assert_shape("FCStd/Airframe", doc.getObject("Airframe").Shape)
assert_shape("FCStd/PropellerDisk", doc.getObject("PropellerDisk").Shape)
App.closeDocument(doc.Name)

step_airframe = Part.read(str(BASE / "exports" / "CargoUAV_airframe.step"))
assert_shape("STEP/Airframe", step_airframe)

step_complete = Part.read(str(BASE / "exports" / "CargoUAV_with_propeller_disk.step"))
assert_shape("STEP/Complete", step_complete, expected_solids=2)

for filename in ("CargoUAV_airframe.stl", "CargoUAV_propeller_disk.stl"):
    mesh = Mesh.Mesh(str(BASE / "exports" / filename))
    if not mesh.isSolid():
        raise RuntimeError(f"{filename}: STL mesh is not solid/closed")
    if mesh.CountFacets == 0:
        raise RuntimeError(f"{filename}: STL has no facets")
    print(
        f"STL/{filename}: solid=True facets={mesh.CountFacets} "
        f"points={mesh.CountPoints} bbox_mm="
        f"({mesh.BoundBox.XLength:.3f}, {mesh.BoundBox.YLength:.3f}, {mesh.BoundBox.ZLength:.3f})"
    )

print("DELIVERY_VALIDATION_OK")

