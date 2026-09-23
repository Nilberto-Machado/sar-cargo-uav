"""Reopen and validate the refined FreeCAD, STEP and STL delivery files."""

from pathlib import Path
import json

import FreeCAD as App
import Mesh
import Part


BASE = Path(__file__).resolve().parent
doc = App.openDocument(str(BASE / "CargoUAV_Refined_CFD.FCStd"))
airframe = doc.getObject("AirframeRefined")
if airframe is None:
    raise RuntimeError("AirframeRefined missing from FCStd")

fc_shape = airframe.Shape
step_shape = Part.read(str(BASE / "exports" / "CargoUAV_Refined_airframe.step"))
stl_mesh = Mesh.Mesh(str(BASE / "exports" / "CargoUAV_Refined_airframe.stl"))

result = {
    "fcstd": {
        "valid": bool(fc_shape.isValid()),
        "closed": bool(fc_shape.isClosed()),
        "solids": len(fc_shape.Solids),
        "bbox_mm": [fc_shape.BoundBox.XLength, fc_shape.BoundBox.YLength, fc_shape.BoundBox.ZLength],
    },
    "step": {
        "valid": bool(step_shape.isValid()),
        "closed": bool(step_shape.isClosed()),
        "solids": len(step_shape.Solids),
        "bbox_mm": [step_shape.BoundBox.XLength, step_shape.BoundBox.YLength, step_shape.BoundBox.ZLength],
    },
    "stl": {
        "facets": stl_mesh.CountFacets,
        "points": stl_mesh.CountPoints,
        "solid": bool(stl_mesh.isSolid()),
        "bbox_mm": [stl_mesh.BoundBox.XLength, stl_mesh.BoundBox.YLength, stl_mesh.BoundBox.ZLength],
    },
}

if not (result["fcstd"]["valid"] and result["fcstd"]["closed"] and result["fcstd"]["solids"] == 1):
    raise RuntimeError(f"FCStd validation failed: {result['fcstd']}")
if not (result["step"]["valid"] and result["step"]["closed"] and result["step"]["solids"] == 1):
    raise RuntimeError(f"STEP validation failed: {result['step']}")
if not result["stl"]["solid"]:
    raise RuntimeError(f"STL validation failed: {result['stl']}")

(BASE / "delivery_validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
