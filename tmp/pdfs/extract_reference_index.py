import json
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(r"E:\OneDrive\09 - Estante Virtual - Livros\Técnicos\Aerodinâmica - Teoria de Voo")
OUT = Path(__file__).resolve().parent
TEXT_DIR = OUT / "book_text"
TEXT_DIR.mkdir(parents=True, exist_ok=True)

BOOKS = {
    "etkin": ROOT / "[Dover Books on Aeronautical Engineering] Bernard Etkin, Engineering - Dynamics of Atmospheric Flight (2005, Dover Publications) - libgen.li.pdf",
    "abbott": ROOT / "[Dover Books on Physics] Ira H. Abbott, A. E. von Doenhoff - Theory of Wing Sections_ Including a Summary of Airfoil Data (1959, Dover Publications) - libgen.l.pdf",
    "raymer": ROOT / "Aircraft Design_ A Conceptual Approach.pdf",
    "performance": ROOT / "Aircraft Performance & Design.pdf",
    "mccormick": ROOT / "Barnes W. McCormick - Aerodynamics, Aeronautics, and Flight Mechanics (1994, Wiley) - libgen.li.pdf",
    "intro_flight": ROOT / "John Anderson Senior Lecturer Dr, Mary L. Bowden Senior Lecturer - Introduction to Flight (2021, McGraw-Hill Education) - libgen.li.pdf",
    "fundamentals": ROOT / "John D. Anderson Jr. - Fundamentals of Aerodynamics (2023, McGraw Hill) - libgen.li.pdf",
}

KEYWORDS = {
    "wing_planform": re.compile(r"\b(aspect ratio|taper ratio|wing loading|elliptic|induced drag|span efficiency)\b", re.I),
    "airfoil": re.compile(r"\b(airfoil|aerofoil|thickness ratio|reynolds number|laminar|maximum lift|stall)\b", re.I),
    "stability": re.compile(r"\b(static margin|neutral point|tail volume|longitudinal stability|directional stability|dihedral effect)\b", re.I),
    "control": re.compile(r"\b(elevator|rudder|aileron|control surface|control effectiveness)\b", re.I),
    "performance": re.compile(r"\b(range|endurance|lift-to-drag|drag polar|specific fuel consumption|propeller efficiency)\b", re.I),
    "configuration": re.compile(r"\b(configuration design|conceptual design|fuselage|empennage|v-tail|landing gear)\b", re.I),
}

def flatten_outline(reader):
    rows = []
    def walk(items, depth=0):
        for item in items:
            if isinstance(item, list):
                walk(item, depth + 1)
                continue
            title = getattr(item, "title", None)
            if not title:
                continue
            try:
                page = reader.get_destination_page_number(item) + 1
            except Exception:
                page = None
            rows.append({"depth": depth, "title": str(title), "page": page})
    try:
        walk(reader.outline)
    except Exception:
        pass
    return rows

def excerpt(text, match, radius=260):
    lo = max(0, match.start() - radius)
    hi = min(len(text), match.end() + radius)
    return re.sub(r"\s+", " ", text[lo:hi]).strip()

summary = {}
for book_id, path in BOOKS.items():
    print(f"Reading {book_id}: {path.name}", flush=True)
    reader = PdfReader(str(path))
    metadata = reader.metadata or {}
    hits = []
    text_path = TEXT_DIR / f"{book_id}.txt"
    with text_path.open("w", encoding="utf-8", newline="\n") as stream:
        for page_no, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception as exc:
                text = f"[TEXT EXTRACTION ERROR: {exc}]"
            stream.write(f"\n\n===== PDF PAGE {page_no} =====\n{text}")
            page_hits = []
            for group, pattern in KEYWORDS.items():
                match = pattern.search(text)
                if match:
                    page_hits.append({"group": group, "term": match.group(0), "excerpt": excerpt(text, match)})
            if page_hits:
                hits.append({"page": page_no, "matches": page_hits})
    summary[book_id] = {
        "path": str(path), "filename": path.name, "pages": len(reader.pages),
        "metadata": {str(k): str(v) for k, v in metadata.items()},
        "outline": flatten_outline(reader), "keyword_pages": hits,
        "text_path": str(text_path),
    }

(OUT / "reference_index.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: {"pages": v["pages"], "hits": len(v["keyword_pages"])} for k, v in summary.items()}, indent=2))
