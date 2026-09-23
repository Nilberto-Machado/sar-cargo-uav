"""Reopen and validate all Hybrid VTOL deliverables independently."""

from pathlib import Path
import FreeCAD as App
import Part
import Mesh

BASE = Path(__file__).resolve().parent


def check_shape(label, shape, solids):
    if not shape.isValid() or not shape.isClosed() or len(shape.Solids) != solids:
        raise RuntimeError(
            f"{label}: valid={shape.isValid()} closed={shape.isClosed()} solids={len(shape.Solids)}"
        )
    bb = shape.BoundBox
    print(f"{label}: OK solids={solids} faces={len(shape.Faces)} "
          f"bbox=({bb.XLength:.2f}, {bb.YLength:.2f}, {bb.ZLength:.2f}) mm")


doc = App.openDocument(str(BASE / "CargoUAV_HybridVTOL_CFD.FCStd"))
check_shape("FCStd/Airframe", doc.getObject("Airframe").Shape, 1)
check_shape("FCStd/PusherDisk", doc.getObject("PusherDisk").Shape, 1)
check_shape("FCStd/VTOLDisks", doc.getObject("VTOLDisks").Shape, 4)
App.closeDocument(doc.Name)

for filename, solids in (
    ("CargoUAV_HybridVTOL_airframe.step", 1),
    ("CargoUAV_HybridVTOL_with_pusher.step", 2),
    ("CargoUAV_HybridVTOL_complete.step", 6),
):
    check_shape("STEP/" + filename, Part.read(str(BASE / "exports" / filename)), solids)

for filename in (
    "CargoUAV_HybridVTOL_airframe.stl",
    "CargoUAV_HybridVTOL_pusher_disk.stl",
    "CargoUAV_HybridVTOL_vtol_disks.stl",
):
    mesh = Mesh.Mesh(str(BASE / "exports" / filename))
    if not mesh.isSolid() or mesh.CountFacets == 0:
        raise RuntimeError(f"{filename}: STL is not a non-empty closed mesh")
    print(f"STL/{filename}: OK facets={mesh.CountFacets} points={mesh.CountPoints}")

print("HYBRID_VTOL_DELIVERY_VALIDATION_OK")

