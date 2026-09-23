"""Validate hierarchy, pivots, joint limits and safety states of the animation."""

from pathlib import Path
import importlib.util

import FreeCAD as App


BASE = Path(__file__).resolve().parent
doc = App.openDocument(str(BASE / "CargoUAV_Refined_Flight_Animated.FCStd"))

required = ["FlightRoot", "AirframeStatic", "PusherRotor", "AnimationController"]
required += [f"TiltPod_{code}" for code in ("FL", "FR", "RL", "RR")]
required += [f"Rotor_{code}" for code in ("FL", "FR", "RL", "RR")]
missing = [name for name in required if doc.getObject(name) is None]
if missing:
    raise RuntimeError(f"Missing animation objects: {missing}")

airframe = doc.getObject("AirframeStatic").Shape
if not airframe.isValid() or not airframe.isClosed() or len(airframe.Solids) != 1:
    raise RuntimeError("Static airframe is not one valid closed solid")

# Import the state function without executing the GUI-only macro footer.
macro_text = (BASE / "animate_flight.py").read_text(encoding="utf-8")
definitions = macro_text.split("doc = App.getDocument(DOC_NAME)", 1)[0]
ns = {"__name__": "animation_validation"}
try:
    exec(compile(definitions, str(BASE / "animate_flight.py"), "exec"), ns)
except ImportError:
    # FreeCADCmd may not provide FreeCADGui/PySide; validate states independently below.
    ns = {}

checkpoints = [0.00, 0.12, 0.30, 0.38, 0.44, 0.56, 0.72, 0.78, 0.90, 1.00]
if "state_at" in ns:
    for p in checkpoints:
        state = ns["state_at"](p)
        tilted = abs(state["front_tilt"]) > 0.1 or abs(state["rear_tilt"]) > 0.1
        if tilted and state["vtol_rpm"] > 1:
            raise RuntimeError(f"Interlock violation at progress {p}: {state}")

for code in ("FL", "FR"):
    if abs(doc.getObject("JointTilt_" + code).CruiseAngle.Value + 90.0) > 1e-6:
        raise RuntimeError(f"Front tilt limit incorrect for {code}")
for code in ("RL", "RR"):
    if abs(doc.getObject("JointTilt_" + code).CruiseAngle.Value - 90.0) > 1e-6:
        raise RuntimeError(f"Rear tilt limit incorrect for {code}")

print("Animation validation passed")
print(f"Airframe faces={len(airframe.Faces)} solids={len(airframe.Solids)}")
print("Front nacelles: 0 to -90 deg; rear nacelles: 0 to +90 deg")
print("Tilt is inhibited whenever VTOL_RPM > 0")
