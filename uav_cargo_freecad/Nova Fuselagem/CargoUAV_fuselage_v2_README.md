# CargoUAV fuselage v2

Mission-compatible fuselage prototype for the SAR cargo UAV.

## Mission envelope

- Overall length: 2,850 mm
- Maximum external width: 520 mm
- Maximum external height: 600 mm
- Payload envelope: 700 × 390 × 310 mm
- Payload containment: 100%
- Payload position: x = 550–1,250 mm, centered at y = 0 mm
- Intended payload: up to 5 kg
- Preliminary CG target retained: x ≈ 1,070 mm

## Geometry

Each cross-section consists of four true analytic elliptical arcs. Adjacent
stations are connected by ruled surfaces so the CAD model cannot overshoot the
specified dimensional envelope. The model contains one closed solid, 38 faces,
76 edges, and 40 vertices.

## Validation

- FreeCAD basic validity: pass
- OpenCASCADE BOP check before export: pass
- STEP export and reimport: pass
- OpenCASCADE BOP check after STEP reimport: pass
- Solids after reimport: 1
- Closed shells after reimport: 1

This is a validated fuselage-only prototype. Wings, V-tail mounting pads,
doors, structural thickness, VTOL interfaces, and pusher installation remain
to be integrated and revalidated incrementally.
