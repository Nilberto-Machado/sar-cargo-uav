"""Build the refined UAV kinematic flight-animation assembly in FreeCAD 1.1+."""

from pathlib import Path
import math

import FreeCAD as App
import Part


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
SOURCE = ROOT / "uav_cargo_refined" / "build_refined_uav.py"
OUTPUT = BASE / "CargoUAV_Refined_Flight_Animated.FCStd"

# Load only geometry definitions.  The delivery/export block is intentionally skipped.
source_text = SOURCE.read_text(encoding="utf-8")
definitions = source_text.split("metrics = design_metrics(P)", 1)[0]
ns = {"__file__": str(SOURCE), "__name__": "refined_geometry_definitions"}
exec(compile(definitions, str(SOURCE), "exec"), ns)

P = ns["P"]
make_fuselage = ns["fuselage"]
make_wing = ns["wing"]
make_vtail = ns["vtail"]
make_wire = ns["closed_wire"]
boom_z = ns["boom_z"]

BOOM_Z = boom_z(P)
PIVOTS = {
    "FL": App.Vector(P["front_motor_x"], -P["boom_y"], BOOM_Z),
    "FR": App.Vector(P["front_motor_x"], P["boom_y"], BOOM_Z),
    "RL": App.Vector(P["rear_motor_x"], -P["boom_y"], BOOM_Z),
    "RR": App.Vector(P["rear_motor_x"], P["boom_y"], BOOM_Z),
}
ROTOR_OFFSET = App.Vector(0, 0, 190)
PUSHER_PIVOT = App.Vector(P["pusher_plane_x"], 0, 25)


def static_booms_and_shafts():
    shapes = []
    length = P["boom_end_x"] - P["boom_start_x"]
    for y in (-P["boom_y"], P["boom_y"]):
        shapes.append(Part.makeCylinder(
            P["boom_radius"], length,
            App.Vector(P["boom_start_x"], y, BOOM_Z), App.Vector(1, 0, 0),
        ))
        for x in (P["front_motor_x"], P["rear_motor_x"]):
            shapes.append(Part.makeCylinder(
                26, 150, App.Vector(x, y - 75, BOOM_Z), App.Vector(0, 1, 0),
            ))
    result = shapes[0]
    for shape in shapes[1:]:
        result = result.fuse(shape)
    return result.removeSplitter()


def local_xy_ellipse(z, width, depth, count=32):
    return make_wire([
        (
            0.5 * depth * math.sin(2.0 * math.pi * i / count),
            0.5 * width * math.cos(2.0 * math.pi * i / count),
            z,
        )
        for i in range(count)
    ])


def nacelle_shape():
    stations = [
        (-160, 14, 14), (-100, 96, 112), (0, 116, 136),
        (100, 96, 112), (160, 14, 14),
    ]
    return Part.makeLoft([local_xy_ellipse(z, width, depth) for z, width, depth in stations], True, False)


def blade_along_x():
    face = Part.Face(make_wire([
        (42, -27, -4.5), (365, -13, -4.5),
        (365, 13, -4.5), (42, 27, -4.5),
    ]))
    return face.extrude(App.Vector(0, 0, 9))


def lift_rotor_shape():
    hub = Part.makeCylinder(40, 48, App.Vector(0, 0, -24), App.Vector(0, 0, 1))
    blade_a = blade_along_x()
    blade_b = blade_a.copy()
    blade_b.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 180)
    return Part.makeCompound([hub, blade_a, blade_b])


def pusher_blade_shape():
    face = Part.Face(make_wire([
        (-4.5, 40, -30), (-4.5, 285, -16),
        (-4.5, 285, 16), (-4.5, 40, 30),
    ]))
    return face.extrude(App.Vector(9, 0, 0))


def pusher_rotor_shape():
    hub = Part.makeCylinder(38, 84, App.Vector(-42, 0, 0), App.Vector(1, 0, 0))
    blade = pusher_blade_shape()
    blades = []
    for angle in (0, 120, 240):
        item = blade.copy()
        item.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), angle)
        blades.append(item)
    return Part.makeCompound([hub] + blades)


def add_color(obj, rgb, transparency=0):
    if App.GuiUp and obj.ViewObject:
        obj.ViewObject.ShapeColor = rgb
        obj.ViewObject.Transparency = transparency


doc = App.newDocument("CargoUAV_Refined_Flight_Animated")

scene = doc.addObject("App::DocumentObjectGroup", "FlightScene")
scene.Label = "Flight animation scene"

ground = doc.addObject("PartDesign::Feature", "Ground")
ground.Label = "Ground reference"
ground.Shape = Part.makeBox(16000, 8000, 100, App.Vector(-13000, -4000, -100))
add_color(ground, (0.36, 0.46, 0.28))
scene.addObject(ground)

runway = doc.addObject("PartDesign::Feature", "Runway")
runway.Label = "VTOL operating area"
runway.Shape = Part.makeBox(16000, 2400, 18, App.Vector(-13000, -1200, 0))
add_color(runway, (0.30, 0.31, 0.33))
scene.addObject(runway)

markings = []
for x in range(-12000, 2000, 1200):
    markings.append(Part.makeBox(500, 70, 8, App.Vector(x, -35, 19)))
runway_marks = doc.addObject("PartDesign::Feature", "RunwayMarkings")
runway_marks.Label = "Runway centre markings"
runway_marks.Shape = Part.makeCompound(markings)
add_color(runway_marks, (0.92, 0.92, 0.88))
scene.addObject(runway_marks)

trajectory_points = [
    App.Vector(0, 0, 420), App.Vector(0, 0, 5420),
    App.Vector(-4000, 0, 6420), App.Vector(-9000, 0, 6420),
    App.Vector(-12000, 0, 420),
]
trajectory = doc.addObject("PartDesign::Feature", "FlightTrajectory")
trajectory.Label = "Illustrative kinematic trajectory"
trajectory.Shape = Part.makePolygon(trajectory_points)
if App.GuiUp and trajectory.ViewObject:
    trajectory.ViewObject.LineColor = (0.95, 0.45, 0.12)
    trajectory.ViewObject.LineWidth = 4.0
scene.addObject(trajectory)

aircraft = doc.addObject("App::Part", "FlightRoot")
aircraft.Label = "Animated aircraft root - translation and pitch"
scene.addObject(aircraft)

airframe_shape = make_fuselage(P).fuse(make_wing(P)).fuse(make_vtail(P)).fuse(static_booms_and_shafts()).removeSplitter()
if not airframe_shape.isValid() or not airframe_shape.isClosed() or len(airframe_shape.Solids) != 1:
    raise RuntimeError(f"Invalid animation airframe: solids={len(airframe_shape.Solids)}")

airframe = doc.addObject("PartDesign::Feature", "AirframeStatic")
airframe.Label = "Refined airframe without moving nacelles"
airframe.Shape = airframe_shape
add_color(airframe, (0.82, 0.85, 0.88))
aircraft.addObject(airframe)

joints = doc.addObject("App::DocumentObjectGroup", "KinematicJoints")
joints.Label = "Explicit tilt and spin joints"

for code, pivot in PIVOTS.items():
    pod = doc.addObject("App::Part", "TiltPod_" + code)
    pod.Label = f"Tilting nacelle {code}"
    pod.Placement.Base = pivot
    aircraft.addObject(pod)

    nacelle = doc.addObject("PartDesign::Feature", "Nacelle_" + code)
    nacelle.Label = f"Streamlined nacelle {code}"
    nacelle.Shape = nacelle_shape()
    add_color(nacelle, (0.25, 0.29, 0.35))
    pod.addObject(nacelle)

    rotor = doc.addObject("App::Part", "Rotor_" + code)
    rotor.Label = f"Spinning lift rotor {code}"
    rotor.Placement.Base = ROTOR_OFFSET
    pod.addObject(rotor)

    blades = doc.addObject("PartDesign::Feature", "RotorBlades_" + code)
    blades.Label = f"Indexed rotor blades {code}"
    blades.Shape = lift_rotor_shape()
    add_color(blades, (0.08, 0.10, 0.13))
    rotor.addObject(blades)

    tilt_joint = doc.addObject("App::FeaturePython", "JointTilt_" + code)
    tilt_joint.Label = f"Revolute tilt joint {code}"
    tilt_joint.addProperty("App::PropertyVector", "Pivot", "Kinematics")
    tilt_joint.Pivot = pivot
    tilt_joint.addProperty("App::PropertyVector", "Axis", "Kinematics")
    tilt_joint.Axis = App.Vector(0, 1, 0)
    tilt_joint.addProperty("App::PropertyAngle", "TakeoffAngle", "Limits")
    tilt_joint.TakeoffAngle = 0
    tilt_joint.addProperty("App::PropertyAngle", "CruiseAngle", "Limits")
    tilt_joint.CruiseAngle = 90 if code.startswith("R") else -90
    tilt_joint.addProperty("App::PropertyString", "Interlock", "Safety")
    tilt_joint.Interlock = "Rotor stopped, indexed at 90 deg and mechanically locked before nacelle rotation"
    tilt_joint.addProperty("App::PropertyLinkGlobal", "MovingPart", "Kinematics")
    tilt_joint.MovingPart = pod
    joints.addObject(tilt_joint)

    spin_joint = doc.addObject("App::FeaturePython", "JointSpin_" + code)
    spin_joint.Label = f"Rotor spin joint {code}"
    spin_joint.addProperty("App::PropertyVector", "AxisInPod", "Kinematics")
    spin_joint.AxisInPod = App.Vector(0, 0, 1)
    spin_joint.addProperty("App::PropertyLinkGlobal", "MovingPart", "Kinematics")
    spin_joint.MovingPart = rotor
    joints.addObject(spin_joint)

pusher = doc.addObject("App::Part", "PusherRotor")
pusher.Label = "Gasoline pusher rotor"
pusher.Placement.Base = PUSHER_PIVOT
aircraft.addObject(pusher)
pusher_blades = doc.addObject("PartDesign::Feature", "PusherBlades")
pusher_blades.Shape = pusher_rotor_shape()
add_color(pusher_blades, (0.12, 0.13, 0.15))
pusher.addObject(pusher_blades)

pusher_joint = doc.addObject("App::FeaturePython", "JointSpinPusher")
pusher_joint.Label = "Pusher spin joint"
pusher_joint.addProperty("App::PropertyVector", "Axis", "Kinematics")
pusher_joint.Axis = App.Vector(1, 0, 0)
pusher_joint.addProperty("App::PropertyLinkGlobal", "MovingPart", "Kinematics")
pusher_joint.MovingPart = pusher
joints.addObject(pusher_joint)

controller = doc.addObject("App::FeaturePython", "AnimationController")
controller.Label = "Flight animation live status"
controller.addProperty("App::PropertyString", "Phase", "Live status")
controller.Phase = "Ready on ground"
controller.addProperty("App::PropertyInteger", "Frame", "Live status")
controller.Frame = 0
controller.addProperty("App::PropertyFloat", "Progress", "Live status")
controller.Progress = 0.0
controller.addProperty("App::PropertyFloat", "Altitude_m", "Live status")
controller.Altitude_m = 0.0
controller.addProperty("App::PropertyFloat", "Distance_m", "Live status")
controller.Distance_m = 0.0
controller.addProperty("App::PropertyFloat", "Speed_mps", "Live status")
controller.Speed_mps = 0.0
controller.addProperty("App::PropertyAngle", "FrontTilt_deg", "Live status")
controller.FrontTilt_deg = 0.0
controller.addProperty("App::PropertyAngle", "RearTilt_deg", "Live status")
controller.RearTilt_deg = 0.0
controller.addProperty("App::PropertyInteger", "VTOL_RPM", "Live status")
controller.VTOL_RPM = 0
controller.addProperty("App::PropertyInteger", "Pusher_RPM", "Live status")
controller.Pusher_RPM = 0
controller.addProperty("App::PropertyString", "InterlockStatus", "Live status")
controller.InterlockStatus = "Tilt locked; rotors safe"
controller.addProperty("App::PropertyString", "SimulationScope", "Documentation")
controller.SimulationScope = "Kinematic visualization only; not 6-DOF flight dynamics or performance validation"
controller.addProperty("App::PropertyString", "RunCommand", "Documentation")
controller.RunCommand = "Macro > Macros > animate_flight.py > Execute"

aircraft.Placement.Base = App.Vector(0, 0, 420)
doc.recompute()
doc.saveAs(str(OUTPUT))
print(f"Saved {OUTPUT}")
print(f"Airframe valid={airframe_shape.isValid()} closed={airframe_shape.isClosed()} solids={len(airframe_shape.Solids)}")
