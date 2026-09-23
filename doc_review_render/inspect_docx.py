from pathlib import Path
from zipfile import ZipFile
import json
from lxml import etree

src = Path(r"E:\OneDrive\08 - Projetos\Arduino\Documentação Projeto Arduino.docx")
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"w": W, "r": R}

def q(tag):
    return f"{{{W}}}{tag}"

with ZipFile(src) as z:
    names = set(z.namelist())
    root = etree.fromstring(z.read("word/document.xml"))
    out = []
    for child in root.find("w:body", NS):
        if child.tag == q("p"):
            texts = child.xpath(".//w:t/text() | .//w:delText/text()", namespaces=NS)
            text = "".join(texts).strip()
            style = child.xpath("string(./w:pPr/w:pStyle/@w:val)", namespaces=NS)
            if text:
                out.append({"type": "paragraph", "style": style, "text": text})
        elif child.tag == q("tbl"):
            rows = []
            for tr in child.findall("w:tr", NS):
                row = []
                for tc in tr.findall("w:tc", NS):
                    row.append(" ".join(t.strip() for t in tc.xpath(".//w:t/text()", namespaces=NS) if t.strip()))
                rows.append(row)
            out.append({"type": "table", "rows": rows})

    rels = []
    rel_name = "word/_rels/document.xml.rels"
    if rel_name in names:
        rr = etree.fromstring(z.read(rel_name))
        for rel in rr:
            rels.append({"type": rel.get("Type", "").split("/")[-1], "target": rel.get("Target")})

    result = {
        "source": str(src),
        "size_bytes": src.stat().st_size,
        "body": out,
        "relationships": rels,
        "media": sorted(n for n in names if n.startswith("word/media/")),
        "has_comments": "word/comments.xml" in names,
        "has_footnotes": "word/footnotes.xml" in names,
        "has_endnotes": "word/endnotes.xml" in names,
        "has_track_changes": bool(root.xpath(".//w:ins | .//w:del", namespaces=NS)),
    }

Path(__file__).with_name("content.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
