"""Headless builder that applies FreeCAD container-scope corrections in memory."""

from pathlib import Path

source_path = Path(__file__).resolve().parent / "uav_cargo_animation" / "build_animation_model.py"
source = source_path.read_text(encoding="utf-8")
source = source.replace('"App::PropertyLink", "ParentBody"', '"App::PropertyLinkGlobal", "ParentBody"')
source = source.replace('"App::PropertyLink", "MovingPart"', '"App::PropertyLinkGlobal", "MovingPart"')
source = source.replace('"App::PropertyLink", "MovingBody"', '"App::PropertyLinkGlobal", "MovingBody"')
source = source.replace(
    'markers = doc.addObject("App::DocumentObjectGroup", "RotationMarkers")',
    'markers = doc.addObject("App::FeaturePython", "RotationMarkers")',
)
source = source.replace("    markers.addObject(marker)\n", "")
source = source.replace("markers.addObject(cg_marker)\n", "")
namespace = {"__file__": str(source_path), "__name__": "__main__"}
exec(compile(source, str(source_path), "exec"), namespace)

