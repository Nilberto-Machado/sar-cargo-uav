"""Render a lightweight SVG preview using FreeCAD's tessellated geometry."""

from pathlib import Path

import FreeCAD as App
from PIL import Image, ImageDraw, ImageFont


BASE = Path(__file__).resolve().parent
MODEL = BASE / "CargoUAV_HybridVTOL_Manufacturable.FCStd"
OUTPUT = BASE / "CargoUAV_HybridVTOL_Manufacturable_preview.svg"
PNG_OUTPUT = OUTPUT.with_suffix(".png")
WIDTH, HEIGHT, MARGIN = 1600, 1000, 60


def placed_shape(obj, placement=None):
    shape = obj.Shape.copy()
    shape.Placement = placement or obj.Placement
    return shape


doc = App.openDocument(str(MODEL))
parts = [(placed_shape(doc.getObject("Airframe_VTail")), "#c9d1dc")]

for code in ("FL", "FR", "RL", "RR"):
    tilt = doc.getObject("TiltPod_" + code)
    nacelle = doc.getObject("Nacelle_" + code)
    rotor = doc.getObject("Rotor_" + code)
    blades = doc.getObject("Rotor_" + code + "_Blades")
    parts.append((placed_shape(nacelle, tilt.Placement.multiply(nacelle.Placement)), "#344256"))
    blade_placement = tilt.Placement.multiply(rotor.Placement).multiply(blades.Placement)
    parts.append((placed_shape(blades, blade_placement), "#16191e"))

pusher = doc.getObject("Rotor_Pusher")
pusher_blades = doc.getObject("Rotor_Pusher_Blades")
parts.append((placed_shape(
    pusher_blades,
    pusher.Placement.multiply(pusher_blades.Placement),
), "#16191e"))

triangles = []
for shape, color in parts:
    vertices, facets = shape.tessellate(7.0)
    for facet in facets:
        xyz = [(vertices[i].x, vertices[i].y, vertices[i].z) for i in facet]
        projected = [
            (0.72 * x + 0.69 * y, -0.30 * x + 0.31 * y + 0.90 * z)
            for x, y, z in xyz
        ]
        depth = sum(x - y + 0.75 * z for x, y, z in xyz) / 3.0
        triangles.append((depth, projected, color))

all_points = [point for _, polygon, _ in triangles for point in polygon]
min_u = min(p[0] for p in all_points)
max_u = max(p[0] for p in all_points)
min_v = min(p[1] for p in all_points)
max_v = max(p[1] for p in all_points)
scale = min((WIDTH - 2 * MARGIN) / (max_u - min_u), (HEIGHT - 2 * MARGIN) / (max_v - min_v))
offset_x = (WIDTH - scale * (min_u + max_u)) / 2
offset_y = (HEIGHT + scale * (min_v + max_v)) / 2

svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
    '<rect width="100%" height="100%" fill="#f5f7fa"/>',
]
for _, polygon, color in sorted(triangles):
    points = " ".join(
        f"{offset_x + scale * u:.1f},{offset_y - scale * v:.1f}" for u, v in polygon
    )
    svg.append(f'<polygon points="{points}" fill="{color}" stroke="#4b5563" stroke-width="0.25"/>')
svg.extend([
    '<text x="48" y="62" font-family="Segoe UI,Arial" font-size="28" fill="#172033">Cargo UAV — fuselagem, asa, 4 tilt-rotors e propulsor traseiro</text>',
    '<text x="48" y="94" font-family="Segoe UI,Arial" font-size="18" fill="#526071">Configuração VTOL • empenagem em V a 40° • vista axonométrica</text>',
    '</svg>',
])
OUTPUT.write_text("\n".join(svg), encoding="utf-8")

image = Image.new("RGB", (WIDTH, HEIGHT), "#f5f7fa")
draw = ImageDraw.Draw(image)
for _, polygon, color in sorted(triangles):
    points = [(offset_x + scale * u, offset_y - scale * v) for u, v in polygon]
    draw.polygon(points, fill=color, outline="#4b5563", width=1)
font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 28)
small_font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 18)
draw.text((48, 32), "Cargo UAV — fuselagem, asa, 4 tilt-rotors e propulsor traseiro", fill="#172033", font=font)
draw.text((48, 72), "Configuração VTOL • empenagem em V a 40° • vista axonométrica", fill="#526071", font=small_font)
image.save(PNG_OUTPUT)

print(f"Saved {OUTPUT}")
print(f"Saved {PNG_OUTPUT}")
App.closeDocument(doc.Name)
