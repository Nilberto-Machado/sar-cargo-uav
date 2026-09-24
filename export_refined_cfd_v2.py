import FreeCAD as App
import Mesh
from pathlib import Path

ROOT = Path(r"C:\GitHub\sar-cargo-uav")
FCSTD = ROOT / "uav_cargo_refined" / "CargoUAV_Refined_CFD.FCStd"
OUT = ROOT / "openfoam" / "cfd_geometry_v2"

OUT.mkdir(parents=True, exist_ok=True)

print("Abrindo:", FCSTD)

doc = App.openDocument(str(FCSTD))

airframe = doc.getObject("AirframeRefined")

if airframe is None:
    raise RuntimeError("Objeto AirframeRefined não encontrado.")

if not hasattr(airframe, "Shape") or airframe.Shape.isNull():
    raise RuntimeError("AirframeRefined não possui Shape válido.")

shape = airframe.Shape

print("Objeto selecionado:", airframe.Name)
print("Label:", airframe.Label)
print("Shape valid:", shape.isValid())
print("Shape closed:", shape.isClosed())
print("Solids:", len(shape.Solids))

bbox = shape.BoundBox
print(
    "BBox CAD mm:",
    bbox.XMin, bbox.YMin, bbox.ZMin,
    bbox.XMax, bbox.YMax, bbox.ZMax
)

linear_deflection = 0.5

vertices, facets = shape.tessellate(linear_deflection)

print("Vertices:", len(vertices))
print("Facets:", len(facets))

mesh_mm = Mesh.Mesh()

for tri in facets:
    p1 = vertices[tri[0]]
    p2 = vertices[tri[1]]
    p3 = vertices[tri[2]]

    mesh_mm.addFacet(
        App.Vector(p1.x, p1.y, p1.z),
        App.Vector(p2.x, p2.y, p2.z),
        App.Vector(p3.x, p3.y, p3.z),
    )

out_mm = OUT / "CargoUAV_cruise_v2_mm.stl"
mesh_mm.write(str(out_mm))

print("STL mm:", out_mm)
print("Facets mm:", mesh_mm.CountFacets)

scale = 0.001

mesh_m = Mesh.Mesh()

for tri in facets:
    p1 = vertices[tri[0]]
    p2 = vertices[tri[1]]
    p3 = vertices[tri[2]]

    mesh_m.addFacet(
        App.Vector(p1.x * scale, p1.y * scale, p1.z * scale),
        App.Vector(p2.x * scale, p2.y * scale, p2.z * scale),
        App.Vector(p3.x * scale, p3.y * scale, p3.z * scale),
    )

out_m = OUT / "CargoUAV_cruise_v2_m.stl"
mesh_m.write(str(out_m))

print("STL m:", out_m)
print("Facets m:", mesh_m.CountFacets)

bb = mesh_m.BoundBox

print(
    "BBox STL m:",
    bb.XMin, bb.YMin, bb.ZMin,
    bb.XMax, bb.YMax, bb.ZMax
)

App.closeDocument(doc.Name)

print("EXPORT_OK")
