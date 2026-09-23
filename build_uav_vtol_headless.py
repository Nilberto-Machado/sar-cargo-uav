"""FreeCADCmd entry point for the Hybrid VTOL model.

FreeCADCmd does not create ViewObject instances. The main generator keeps the
visibility hint for normal FreeCAD GUI use; this wrapper removes that one GUI-only
line in memory before executing the otherwise identical parametric generator.
"""

from pathlib import Path

generator = Path(__file__).resolve().parent / "uav_cargo_vtol" / "build_uav_vtol.py"
source = generator.read_text(encoding="utf-8")
source = source.replace("    obj.ViewObject.Visibility = False\n", "")
namespace = {"__file__": str(generator), "__name__": "__main__"}
exec(compile(source, str(generator), "exec"), namespace)

