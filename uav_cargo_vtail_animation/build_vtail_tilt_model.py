"""Build the corrected V-tail and tilting-rotor animation assembly."""

from pathlib import Path
import math
import FreeCAD as App
import Part

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
PARAMETRIC_SOURCE = ROOT / "uav_cargo_vtol" / "build_uav_vtol.py"
OUTPUT = BASE / "CargoUAV_HybridVTOL_VTail_TiltRotor_Animated.FCStd"

# Reuse the validated fuselage and main-wing construction functions without executing
# the delivery section of the source generator.
source = PARAMETRIC_SOURCE.read_text(encoding="utf-8")
definitions = source.split('doc = App.newDocument("CargoUAV_HybridVTOL_CFD")', 1)[0]
ns = {"__file__": str(PARAMETRIC_SOURCE), "__name__": "geometry_definitions"}
exec(compile(definitions, str(PARAMETRIC_SOURCE), "exec"), ns)
P = ns["P"]
make_fuselage = ns["fuselage"]
make_wing = ns["wing"]
make_wire = ns["wire"]

BOOM_Z = 30 + max(P["boom_y"] - 280, 0) * math.tan(math.radians(2))
TILT_PIVOTS = {
    "FL": App.Vector(P["front_motor_x"], -P["boom_y"], BOOM_Z),
    "FR": App.Vector(P["front_motor_x"], P["boom_y"], BOOM_Z),
    "RL": App.Vector(P["rear_motor_x"], -P["boom_y"], BOOM_Z),
    "RR": App.Vector(P["rear_motor_x"], P["boom_y"], BOOM_Z),
}
ROTOR_OFFSET = App.Vector(0, 0, 167)
PUSHER_PIVOT = App.Vector(2960, 0, 20)
CG = App.Vector(1350, 0, 0)


def naca_vtail_section(span_sign, s, half_span=780.0, angle_deg=40.0, count=20):
    angle = math.radians(angle_deg)
    frac = s / half_span
    chord = 520 + frac * (300 - 520)
    xle = 2180 + frac * (2240 - 2180)
    y0 = span_sign * (90 + s * math.cos(angle))
    z0 = 75 + s * math.sin(angle)
    # Normal to each V-tail panel in the YZ plane.
    ny = -span_sign * math.sin(angle)
    nz = math.cos(angle)
    upper, lower = [], []
    for i in range(count + 1):
        beta = math.pi * i / count
        xc = 0.5 * (1 - math.cos(beta))
        yt = 5 * 0.10 * chord * (
            0.2969 * math.sqrt(max(xc, 0)) - 0.1260 * xc
            - 0.3516 * xc**2 + 0.2843 * xc**3 - 0.1036 * xc**4
        )
        upper.append((xle + xc * chord, y0 + ny * yt, z0 + nz * yt))
        lower.append((xle + xc * chord, y0 - ny * yt, z0 - nz * yt))
    return make_wire(upper + list(reversed(lower[1:-1])))


def make_vtail():
    halves = []
    for sign in (-1, 1):
        sections = [naca_vtail_section(sign, s) for s in (0, 390, 780)]
        halves.append(Part.makeLoft(sections, True, False))
    return halves[0].fuse(halves[1])


def make_booms_and_tilt_shafts():
    parts = []
    length = P["boom_end_x"] - P["boom_start_x"]
    for y in (-P["boom_y"], P["boom_y"]):
        parts.append(Part.makeCylinder(
            P["boom_radius"], length,
            App.Vector(P["boom_start_x"], y, BOOM_Z), App.Vector(1, 0, 0)
        ))
        for x in (P["front_motor_x"], P["rear_motor_x"]):
            parts.append(Part.makeCylinder(
                25, 150, App.Vector(x, y - 75, BOOM_Z), App.Vector(0, 1, 0)
            ))
    shape = parts[0]
    for part in parts[1:]:
        shape = shape.fuse(part)
    return shape.removeSplitter()


def nacelle_shape():
    pod = Part.makeCylinder(72, 180, App.Vector(0, 0, -75), App.Vector(0, 0, 1))
    motor = Part.makeCylinder(48, 62, App.Vector(0, 0, 105), App.Vector(0, 0, 1))
    return pod.fuse(motor)


def lift_rotor_shape():
    hub = Part.makeCylinder(38, 44, App.Vector(0, 0, -22), App.Vector(0, 0, 1))
    a = Part.makeBox(320, 52, 9, App.Vector(42, -26, -4.5))
    b = Part.makeBox(320, 52, 9, App.Vector(-362, -26, -4.5))
    return Part.makeCompound([hub, a, b])


def pusher_shape():
    hub = Part.makeCylinder(36, 80, App.Vector(-40, 0, 0), App.Vector(1, 0, 0))
    a = Part.makeBox(9, 230, 48, App.Vector(-4.5, 40, -24))
    b = Part.makeBox(9, 230, 48, App.Vector(-4.5, -270, -24))
    return Part.makeCompound([hub, a, b])


def color(obj, rgb, transparency=0):
    if App.GuiUp and obj.ViewObject:
        obj.ViewObject.ShapeColor = rgb
        obj.ViewObject.Transparency = transparency


doc = App.newDocument("CargoUAV_HybridVTOL_VTail_TiltRotor_Animated")
assembly = doc.addObject("App::Part", "AircraftAssembly")
assembly.Label = "Aircraft rigid-body assembly"

airframe_shape = make_fuselage(P).fuse(make_wing(P)).fuse(make_vtail()).fuse(make_booms_and_tilt_shafts()).removeSplitter()
if not airframe_shape.isValid() or not airframe_shape.isClosed() or len(airframe_shape.Solids) != 1:
    raise RuntimeError(f"Invalid V-tail airframe: solids={len(airframe_shape.Solids)}")
airframe = doc.addObject("PartDesign::Feature", "Airframe_VTail")
airframe.Label = "Watertight airframe with V-tail and tilt shafts"
airframe.Shape = airframe_shape
assembly.addObject(airframe)
color(airframe, (0.82, 0.84, 0.88))

joints = doc.addObject("App::DocumentObjectGroup", "KinematicJoints")
joints.Label = "Tilt and spin joints"

for code, pivot in TILT_PIVOTS.items():
    tilt = doc.addObject("App::Part", "TiltPod_" + code)
    tilt.Label = f"Tilting nacelle {code}"
    tilt.Placement.Base = pivot
    assembly.addObject(tilt)

    pod = doc.addObject("PartDesign::Feature", "Nacelle_" + code)
    pod.Shape = nacelle_shape()
    tilt.addObject(pod)
    color(pod, (0.25, 0.28, 0.34))

    rotor = doc.addObject("App::Part", "Rotor_" + code)
    rotor.Label = f"Spinning rotor {code}"
    rotor.Placement.Base = ROTOR_OFFSET
    tilt.addObject(rotor)
    blade = doc.addObject("PartDesign::Feature", "Rotor_" + code + "_Blades")
    blade.Shape = lift_rotor_shape()
    rotor.addObject(blade)
    color(blade, (0.10, 0.12, 0.15))

    tilt_joint = doc.addObject("App::FeaturePython", "Joint_Tilt_" + code)
    tilt_joint.Label = f"Revolute tilt joint {code}"
    tilt_joint.addProperty("App::PropertyVector", "PivotLocal", "Kinematics")
    tilt_joint.PivotLocal = pivot
    tilt_joint.addProperty("App::PropertyVector", "AxisLocal", "Kinematics")
    tilt_joint.AxisLocal = App.Vector(0, 1, 0)
    tilt_joint.addProperty("App::PropertyAngle", "TakeoffAngle", "Limits")
    tilt_joint.TakeoffAngle = 0
    tilt_joint.addProperty("App::PropertyAngle", "CruiseAngle", "Limits")
    tilt_joint.CruiseAngle = -90
    tilt_joint.addProperty("App::PropertyLinkGlobal", "MovingPart", "Kinematics")
    tilt_joint.MovingPart = tilt
    tilt_joint.addProperty("App::PropertyString", "Constraint", "Kinematics")
    tilt_joint.Constraint = "All translation locked; only rotation about local +Y, range 0 to -90 deg"
    joints.addObject(tilt_joint)

    spin_joint = doc.addObject("App::FeaturePython", "Joint_Spin_" + code)
    spin_joint.Label = f"Rotor spin joint {code}"
    spin_joint.addProperty("App::PropertyVector", "PivotInTiltPod", "Kinematics")
    spin_joint.PivotInTiltPod = ROTOR_OFFSET
    spin_joint.addProperty("App::PropertyVector", "AxisInTiltPod", "Kinematics")
    spin_joint.AxisInTiltPod = App.Vector(0, 0, 1)
    spin_joint.addProperty("App::PropertyLinkGlobal", "ParentTiltPod", "Kinematics")
    spin_joint.ParentTiltPod = tilt
    spin_joint.addProperty("App::PropertyLinkGlobal", "MovingPart", "Kinematics")
    spin_joint.MovingPart = rotor
    spin_joint.addProperty("App::PropertyString", "Constraint", "Kinematics")
    spin_joint.Constraint = "Revolute spin about pod-local +Z; axis follows nacelle tilt"
    joints.addObject(spin_joint)

pusher = doc.addObject("App::Part", "Rotor_Pusher")
pusher.Label = "Gasoline pusher rotor"
pusher.Placement.Base = PUSHER_PIVOT
assembly.addObject(pusher)
pusher_blades = doc.addObject("PartDesign::Feature", "Rotor_Pusher_Blades")
pusher_blades.Shape = pusher_shape()
pusher.addObject(pusher_blades)
color(pusher_blades, (0.10, 0.12, 0.15))

pusher_joint = doc.addObject("App::FeaturePython", "Joint_Spin_Pusher")
pusher_joint.Label = "Pusher spin joint"
pusher_joint.addProperty("App::PropertyVector", "PivotLocal", "Kinematics")
pusher_joint.PivotLocal = PUSHER_PIVOT
pusher_joint.addProperty("App::PropertyVector", "AxisLocal", "Kinematics")
pusher_joint.AxisLocal = App.Vector(1, 0, 0)
pusher_joint.addProperty("App::PropertyLinkGlobal", "MovingPart", "Kinematics")
pusher_joint.MovingPart = pusher
joints.addObject(pusher_joint)

cg_joint = doc.addObject("App::FeaturePython", "Joint_AircraftCG")
cg_joint.Label = "Aircraft CG and pitch reference"
cg_joint.addProperty("App::PropertyVector", "CGLocal", "Kinematics")
cg_joint.CGLocal = CG
cg_joint.addProperty("App::PropertyVector", "PitchAxisLocal", "Kinematics")
cg_joint.PitchAxisLocal = App.Vector(0, 1, 0)
cg_joint.addProperty("App::PropertyLinkGlobal", "MovingBody", "Kinematics")
cg_joint.MovingBody = assembly
joints.addObject(cg_joint)

# Markers: yellow tilt axes, cyan rotor axes, red CG axis.
for code, pivot in TILT_PIVOTS.items():
    marker = doc.addObject("PartDesign::Feature", "Marker_Tilt_" + code)
    marker.Shape = Part.makeCompound([
        Part.makeSphere(22, pivot),
        Part.makeCylinder(7, 260, pivot - App.Vector(0, 130, 0), App.Vector(0, 1, 0)),
    ])
    assembly.addObject(marker)
    color(marker, (1.0, 0.72, 0.05), 10)

cg_marker = doc.addObject("PartDesign::Feature", "Marker_CG")
cg_marker.Shape = Part.makeCompound([
    Part.makeSphere(34, CG),
    Part.makeCylinder(8, 500, CG - App.Vector(0, 250, 0), App.Vector(0, 1, 0)),
])
assembly.addObject(cg_marker)
color(cg_marker, (0.95, 0.12, 0.10), 5)

scene = doc.addObject("App::DocumentObjectGroup", "Scene")
ground = doc.addObject("PartDesign::Feature", "GroundPlane")
ground.Shape = Part.makeBox(6800, 5000, 20, App.Vector(-3200, -2500, -80))
scene.addObject(ground)
color(ground, (0.62, 0.68, 0.58), 80)

state = doc.addObject("App::FeaturePython", "AnimationState")
state.addProperty("App::PropertyFloat", "SimulationTime", "State")
state.addProperty("App::PropertyString", "Phase", "State")
state.Phase = "Stopped"
state.addProperty("App::PropertyLength", "Altitude", "State")
state.addProperty("App::PropertyAngle", "Pitch", "State")
state.addProperty("App::PropertyAngle", "TiltAngle", "State")
state.addProperty("App::PropertyInteger", "VTOL_RPM", "State")
state.addProperty("App::PropertyInteger", "Pusher_RPM", "State")
state.addProperty("App::PropertyFloat", "AnimationSpeed", "Controls")
state.AnimationSpeed = 1.0
state.addProperty("App::PropertyBool", "Loop", "Controls")
state.Loop = True
state.addProperty("App::PropertyString", "Scope", "Notes")
state.Scope = "Kinematic visualization only; no aerodynamic or flight-dynamics solution"

doc.recompute()
doc.saveAs(str(OUTPUT))
print(f"Saved {OUTPUT}")
print(f"V-tail angle: 40 deg; CG={CG}; boom Z={BOOM_Z:.3f} mm")
for code, pivot in TILT_PIVOTS.items():
    print(f"{code}: tilt pivot={pivot}, axis=(0,1,0); rotor offset={ROTOR_OFFSET}, spin axis=(0,0,1)")

