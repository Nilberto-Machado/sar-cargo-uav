"""Check internal-envelope containment and wing/CG geometry."""

from pathlib import Path
import FreeCAD as App
import Part

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "uav_cargo_vtol" / "build_uav_vtol.py"
source = SOURCE.read_text(encoding="utf-8")
defs = source.split('doc = App.newDocument("CargoUAV_HybridVTOL_CFD")', 1)[0]
ns = {"__file__": str(SOURCE), "__name__": "defs"}
exec(compile(defs, str(SOURCE), "exec"), ns)
P, make_fuselage = ns["P"], ns["fuselage"]
fuse = make_fuselage(P)

envelopes = {
    "payload": Part.makeBox(700, 400, 320, App.Vector(560, -200, -170)),
    "vtol_battery": Part.makeBox(380, 240, 150, App.Vector(1350, -120, -120)),
    "fuel_4L": Part.makeCylinder(65, 300, App.Vector(1780, 0, -45), App.Vector(1, 0, 0)),
    "starter_generator": Part.makeCylinder(65, 130, App.Vector(2540, 0, 20), App.Vector(1, 0, 0)),
}

for name, shape in envelopes.items():
    inside = fuse.common(shape).Volume
    ratio = inside / shape.Volume if shape.Volume else 0
    print(f"{name}: envelope={shape.Volume/1e6:.3f} L inside={inside/1e6:.3f} L containment={100*ratio:.2f}%")

cr = P["wing_root_chord"]
ct = P["wing_tip_chord"]
lam = ct / cr
b = P["span"]
mac = (2/3) * cr * (1 + lam + lam**2) / (1 + lam)
y_mac = (b/6) * (1 + 2*lam) / (1 + lam)
xle_mac = P["wing_root_le_x"] + (P["wing_tip_le_x"] - P["wing_root_le_x"]) * (y_mac / (b/2))
print(f"wing_area={0.5*(cr+ct)*b/1e6:.3f} m2")
print(f"MAC={mac:.1f} mm y_MAC={y_mac:.1f} mm xLE_MAC={xle_mac:.1f} mm")
for frac in (0.20, 0.25, 0.30, 0.35):
    print(f"CG_at_{int(frac*100)}pct_MAC: x={xle_mac + frac*mac:.1f} mm")
print("current_animation_CG: x=1350.0 mm")

