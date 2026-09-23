"""Build the FreeCAD assembly used by the Hybrid VTOL kinematic animation."""

from pathlib import Path
import FreeCAD as App
import Part

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parent
SOURCE = PROJECT / "uav_cargo_vtol" / "CargoUAV_HybridVTOL_CFD.FCStd"
OUTPUT = BASE / "CargoUAV_HybridVTOL_Animated.FCStd"

PIVOTS = {
    "Rotor_VTOL_FL": (App.Vector(600, -950, 220), App.Vector(0, 0, 1), "front left"),
    "Rotor_VTOL_FR": (App.Vector(600, 950, 220), App.Vector(0, 0, 1), "front right"),
    "Rotor_VTOL_RL": (App.Vector(1850, -950, 220), App.Vector(0, 0, 1), "rear left"),
    "Rotor_VTOL_RR": (App.Vector(1850, 950, 220), App.Vector(0, 0, 1), "rear right"),
    "Rotor_Pusher": (App.Vector(2960, 0, 20), App.Vector(1, 0, 0), "gasoline pusher"),
}
CG = App.Vector(1350, 0, 0)


def vtol_rotor_shape():
    hub = Part.makeCylinder(38, 44, App.Vector(0, 0, -22), App.Vector(0, 0, 1))
    blade_a = Part.makeBox(320, 52, 9, App.Vector(42, -26, -4.5))
    blade_b = Part.makeBox(320, 52, 9, App.Vector(-362, -26, -4.5))
    return Part.makeCompound([hub, blade_a, blade_b])


def pusher_rotor_shape():
    hub = Part.makeCylinder(36, 80, App.Vector(-40, 0, 0), App.Vector(1, 0, 0))
    blade_a = Part.makeBox(9, 230, 48, App.Vector(-4.5, 40, -24))
    blade_b = Part.makeBox(9, 230, 48, App.Vector(-4.5, -270, -24))
    return Part.makeCompound([hub, blade_a, blade_b])


def set_view(obj, color, transparency=0):
    if App.GuiUp and obj.ViewObject:
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.LineColor = tuple(max(c - 0.25, 0.0) for c in color)
        obj.ViewObject.Transparency = transparency


source_doc = App.openDocument(str(SOURCE))
source_shape = source_doc.getObject("Airframe").Shape.copy()
App.closeDocument(source_doc.Name)

doc = App.newDocument("CargoUAV_HybridVTOL_Animated")
assembly = doc.addObject("App::Part", "AircraftAssembly")
assembly.Label = "Aircraft assembly — animated rigid body"

airframe = doc.addObject("PartDesign::Feature", "Airframe")
airframe.Label = "Hybrid VTOL airframe"
airframe.Shape = source_shape
assembly.addObject(airframe)
set_view(airframe, (0.82, 0.84, 0.88))

rotor_shape = vtol_rotor_shape()
pusher_shape = pusher_rotor_shape()
rotors = {}
for name, (pivot, axis, label) in PIVOTS.items():
    rotor_part = doc.addObject("App::Part", name)
    rotor_part.Label = f"Rotor — {label}"
    rotor_part.Placement.Base = pivot
    blade = doc.addObject("PartDesign::Feature", name + "_Blades")
    blade.Label = f"Hub and blades — {label}"
    blade.Shape = pusher_shape if name == "Rotor_Pusher" else rotor_shape
    rotor_part.addObject(blade)
    assembly.addObject(rotor_part)
    set_view(blade, (0.15, 0.18, 0.22))
    rotors[name] = rotor_part

# The joint records are explicit and inspectable in the FreeCAD property editor.
joints_group = doc.addObject("App::DocumentObjectGroup", "KinematicJoints")
joints_group.Label = "Joints and rotation points"
for name, (pivot, axis, label) in PIVOTS.items():
    joint = doc.addObject("App::FeaturePython", "Joint_" + name)
    joint.Label = f"Revolute joint — {label}"
    joint.addProperty("App::PropertyString", "JointType", "Kinematics")
    joint.JointType = "Revolute, one rotational degree of freedom"
    joint.addProperty("App::PropertyVector", "PivotLocal", "Kinematics")
    joint.PivotLocal = pivot
    joint.addProperty("App::PropertyVector", "RotationAxisLocal", "Kinematics")
    joint.RotationAxisLocal = axis
    joint.addProperty("App::PropertyLink", "ParentBody", "Kinematics")
    joint.ParentBody = assembly
    joint.addProperty("App::PropertyLink", "MovingPart", "Kinematics")
    joint.MovingPart = rotors[name]
    joint.addProperty("App::PropertyString", "Constraint", "Kinematics")
    joint.Constraint = "Translation locked in X/Y/Z; rotation locked except about RotationAxisLocal"
    joints_group.addObject(joint)

body_joint = doc.addObject("App::FeaturePython", "Joint_AircraftCG")
body_joint.Label = "Aircraft reference — centre of gravity and pitch axis"
body_joint.addProperty("App::PropertyVector", "CGLocal", "Kinematics")
body_joint.CGLocal = CG
body_joint.addProperty("App::PropertyVector", "PitchAxisLocal", "Kinematics")
body_joint.PitchAxisLocal = App.Vector(0, 1, 0)
body_joint.addProperty("App::PropertyString", "DegreesOfFreedom", "Kinematics")
body_joint.DegreesOfFreedom = "Animation: vertical Z, forward -X and pitch about local +Y through CG"
body_joint.addProperty("App::PropertyLink", "MovingBody", "Kinematics")
body_joint.MovingBody = assembly
joints_group.addObject(body_joint)

# Visible axes and pivot markers move with the aircraft because they belong to the assembly.
markers = doc.addObject("App::DocumentObjectGroup", "RotationMarkers")
markers.Label = "Rotation axes and pivot points"
for name, (pivot, axis, label) in PIVOTS.items():
    marker = doc.addObject("PartDesign::Feature", "Marker_" + name)
    marker.Label = f"Axis marker — {label}"
    if abs(axis.z) > 0.5:
        rod = Part.makeCylinder(7, 260, pivot - App.Vector(0, 0, 130), axis)
    else:
        rod = Part.makeCylinder(7, 260, pivot - App.Vector(130, 0, 0), axis)
    marker.Shape = Part.makeCompound([Part.makeSphere(24, pivot), rod])
    markers.addObject(marker)
    assembly.addObject(marker)
    set_view(marker, (1.0, 0.72, 0.05), 10)

cg_marker = doc.addObject("PartDesign::Feature", "Marker_CG")
cg_marker.Label = "Centre of gravity marker and pitch axis"
cg_marker.Shape = Part.makeCompound([
    Part.makeSphere(34, CG),
    Part.makeCylinder(8, 500, CG - App.Vector(0, 250, 0), App.Vector(0, 1, 0)),
])
assembly.addObject(cg_marker)
markers.addObject(cg_marker)
set_view(cg_marker, (0.95, 0.15, 0.12), 5)

# Static scene reference: large enough to keep the full flight path in view.
scene = doc.addObject("App::DocumentObjectGroup", "SceneReferences")
ground = doc.addObject("PartDesign::Feature", "GroundPlane")
ground.Label = "Ground reference"
ground.Shape = Part.makeBox(6800, 5000, 20, App.Vector(-3200, -2500, -80))
scene.addObject(ground)
set_view(ground, (0.62, 0.68, 0.58), 80)

path = doc.addObject("PartDesign::Feature", "FlightPath")
path.Label = "Illustrative animation path"
path.Shape = Part.makePolygon([
    App.Vector(CG.x, 0, 0), App.Vector(CG.x, 0, 1700), App.Vector(CG.x - 2800, 0, 1700)
])
scene.addObject(path)
set_view(path, (0.15, 0.45, 0.95))

state = doc.addObject("App::FeaturePython", "AnimationState")
state.Label = "Animation state and controls"
state.addProperty("App::PropertyFloat", "SimulationTime", "State")
state.addProperty("App::PropertyString", "Phase", "State")
state.Phase = "Stopped at ground"
state.addProperty("App::PropertySpeed", "VerticalSpeed", "State")
state.addProperty("App::PropertySpeed", "ForwardSpeed", "State")
state.addProperty("App::PropertyLength", "Altitude", "State")
state.addProperty("App::PropertyAngle", "Pitch", "State")
state.addProperty("App::PropertyInteger", "VTOL_RPM", "State")
state.addProperty("App::PropertyInteger", "Pusher_RPM", "State")
state.addProperty("App::PropertyFloat", "AnimationSpeed", "Controls")
state.AnimationSpeed = 1.0
state.addProperty("App::PropertyBool", "Loop", "Controls")
state.Loop = True
state.addProperty("App::PropertyString", "ModelScope", "Notes")
state.ModelScope = "Kinematic visualization only — not a flight-dynamics, structural or aerodynamic solution"
state.addProperty("App::PropertyString", "StartMethod", "Notes")
state.StartMethod = "Pusher spin-up represents windmill/starter-generator start; VTOL remains active until RPM is confirmed"

doc.recompute()
doc.saveAs(str(OUTPUT))
print(f"Saved {OUTPUT}")
print("Joints:")
for name, (pivot, axis, label) in PIVOTS.items():
    print(f"  {name}: pivot={pivot} mm axis={axis} parent=AircraftAssembly")
print(f"  Aircraft CG: pivot={CG} mm pitch axis=(0,1,0)")

