"""FreeCAD GUI macro: takeoff, transition, cruise, approach and landing."""

import builtins
import math

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore

try:
    from pivy import coin
except Exception:
    coin = None


DOC_NAME = "CargoUAV_Refined_Flight_Animated"
TOTAL_FRAMES = 420
FPS = 30.0
DT = 1.0 / FPS
BASE_Z = 420.0
PIVOTS = {
    "FL": App.Vector(600, -950, 81.16),
    "FR": App.Vector(600, 950, 81.16),
    "RL": App.Vector(2000, -950, 81.16),
    "RR": App.Vector(2000, 950, 81.16),
}
ROTOR_OFFSET = App.Vector(0, 0, 190)
PUSHER_PIVOT = App.Vector(3065, 0, 25)


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def smooth(value):
    value = clamp(value)
    return value * value * (3.0 - 2.0 * value)


def ramp(progress, start, end, a, b):
    if progress <= start:
        return a
    if progress >= end:
        return b
    return a + (b - a) * smooth((progress - start) / (end - start))


def state_at(progress):
    p = clamp(progress)
    if p < 0.06:
        phase = "Pre-flight checks and VTOL arming"
        altitude = 0.0
        distance = 0.0
        speed = 0.0
        vtol_rpm = ramp(p, 0.00, 0.06, 0, 700)
        pusher_rpm = 0
        pitch = 0.0
        front_tilt = rear_tilt = 0.0
        interlock = "Nacelles vertical and locked"
    elif p < 0.25:
        phase = "Vertical takeoff"
        altitude = ramp(p, 0.06, 0.25, 0.0, 5.0)
        distance = 0.0
        speed = 0.0
        vtol_rpm = ramp(p, 0.06, 0.10, 700, 2800)
        pusher_rpm = 0
        pitch = 0.0
        front_tilt = rear_tilt = 0.0
        interlock = "Nacelles vertical and locked"
    elif p < 0.36:
        phase = "Windmill start of gasoline engine and acceleration"
        altitude = ramp(p, 0.25, 0.36, 5.0, 6.0)
        distance = ramp(p, 0.25, 0.36, 0.0, 3.0)
        speed = ramp(p, 0.25, 0.36, 0.0, 18.0)
        vtol_rpm = ramp(p, 0.30, 0.36, 2800, 600)
        pusher_rpm = ramp(p, 0.25, 0.36, 200, 2200)
        pitch = ramp(p, 0.25, 0.31, 0.0, 7.0)
        front_tilt = rear_tilt = 0.0
        interlock = "Tilt locked while lift rotors are spinning"
    elif p < 0.40:
        phase = "VTOL rotor stop, index and mechanical lock"
        altitude = 6.0
        distance = ramp(p, 0.36, 0.40, 3.0, 4.0)
        speed = ramp(p, 0.36, 0.40, 18.0, 21.0)
        vtol_rpm = ramp(p, 0.36, 0.385, 600, 0)
        pusher_rpm = ramp(p, 0.36, 0.40, 2200, 5200)
        pitch = ramp(p, 0.36, 0.40, 7.0, 3.0)
        front_tilt = rear_tilt = 0.0
        interlock = "Rotors stopping; tilt remains inhibited"
    elif p < 0.48:
        phase = "Safe nacelle transition: front forward, rear aft"
        altitude = 6.0
        distance = ramp(p, 0.40, 0.48, 4.0, 5.5)
        speed = 21.0
        vtol_rpm = 0
        pusher_rpm = 5200
        pitch = ramp(p, 0.40, 0.48, 3.0, 0.0)
        front_tilt = ramp(p, 0.40, 0.48, 0.0, -90.0)
        rear_tilt = ramp(p, 0.40, 0.48, 0.0, 90.0)
        interlock = "Rotors indexed at 90 deg, stopped and locked"
    elif p < 0.68:
        phase = "Wing-borne cruise"
        altitude = 6.0
        distance = ramp(p, 0.48, 0.68, 5.5, 10.0)
        speed = 21.0
        vtol_rpm = 0
        pusher_rpm = 5200
        pitch = 0.0
        front_tilt = -90.0
        rear_tilt = 90.0
        interlock = "VTOL rotors stopped; gasoline pusher active"
    elif p < 0.76:
        phase = "Approach: stopped rotors return to vertical"
        altitude = ramp(p, 0.68, 0.76, 6.0, 5.0)
        distance = ramp(p, 0.68, 0.76, 10.0, 11.0)
        speed = ramp(p, 0.68, 0.76, 21.0, 16.0)
        vtol_rpm = 0
        pusher_rpm = ramp(p, 0.68, 0.76, 5200, 4000)
        pitch = ramp(p, 0.68, 0.76, 0.0, 5.0)
        front_tilt = ramp(p, 0.68, 0.76, -90.0, 0.0)
        rear_tilt = ramp(p, 0.68, 0.76, 90.0, 0.0)
        interlock = "Rotors indexed, stopped and locked during return"
    elif p < 0.80:
        phase = "Vertical-lock confirmation and VTOL restart"
        altitude = 5.0
        distance = ramp(p, 0.76, 0.80, 11.0, 11.3)
        speed = ramp(p, 0.76, 0.80, 16.0, 3.0)
        vtol_rpm = ramp(p, 0.76, 0.80, 0, 2200)
        pusher_rpm = ramp(p, 0.76, 0.80, 4000, 1000)
        pitch = ramp(p, 0.76, 0.80, 5.0, 0.0)
        front_tilt = rear_tilt = 0.0
        interlock = "Nacelles vertical and mechanically locked"
    elif p < 0.98:
        phase = "Vertical descent and landing"
        altitude = ramp(p, 0.80, 0.98, 5.0, 0.0)
        distance = ramp(p, 0.80, 0.98, 11.3, 12.0)
        speed = ramp(p, 0.80, 0.86, 3.0, 0.0)
        vtol_rpm = ramp(p, 0.94, 0.98, 2200, 900)
        pusher_rpm = ramp(p, 0.80, 0.86, 1000, 0)
        pitch = 0.0
        front_tilt = rear_tilt = 0.0
        interlock = "Nacelles vertical and locked"
    else:
        phase = "Landed - propulsion shutdown"
        altitude = 0.0
        distance = 12.0
        speed = 0.0
        vtol_rpm = ramp(p, 0.98, 1.0, 900, 0)
        pusher_rpm = 0
        pitch = 0.0
        front_tilt = rear_tilt = 0.0
        interlock = "All propulsion stopped; tilt locked"
    return {
        "phase": phase, "altitude": altitude, "distance": distance,
        "speed": speed, "vtol_rpm": vtol_rpm, "pusher_rpm": pusher_rpm,
        "pitch": pitch, "front_tilt": front_tilt, "rear_tilt": rear_tilt,
        "interlock": interlock,
    }


class FlightAnimation:
    def __init__(self, document):
        self.doc = document
        self.frame = 0
        self.vtol_angle = 0.0
        self.pusher_angle = 0.0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.step)
        self.timer.setInterval(round(1000.0 / FPS))
        self.view = Gui.activeDocument().activeView()
        Gui.activeDocument().activeView().setAnimationEnabled(True)
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(document.getObject("AnimationController"))
        self.apply(0.0)

    def apply(self, progress):
        state = state_at(progress)
        if (abs(state["front_tilt"]) > 0.1 or abs(state["rear_tilt"]) > 0.1) and state["vtol_rpm"] > 1:
            raise RuntimeError("Safety interlock violation: nacelle tilt with spinning VTOL rotor")

        x = -1000.0 * state["distance"]
        z = BASE_Z + 1000.0 * state["altitude"]
        root = self.doc.getObject("FlightRoot")
        root.Placement = App.Placement(
            App.Vector(x, 0, z),
            App.Rotation(App.Vector(0, 1, 0), state["pitch"]),
        )

        if 0.385 <= progress <= 0.80:
            self.vtol_angle = 90.0
        else:
            self.vtol_angle = (self.vtol_angle + state["vtol_rpm"] / 60.0 * 360.0 * DT) % 360.0
        self.pusher_angle = (self.pusher_angle + state["pusher_rpm"] / 60.0 * 360.0 * DT) % 360.0

        for code, pivot in PIVOTS.items():
            angle = state["rear_tilt"] if code.startswith("R") else state["front_tilt"]
            pod = self.doc.getObject("TiltPod_" + code)
            pod.Placement = App.Placement(pivot, App.Rotation(App.Vector(0, 1, 0), angle))
            rotor = self.doc.getObject("Rotor_" + code)
            rotor.Placement = App.Placement(
                ROTOR_OFFSET, App.Rotation(App.Vector(0, 0, 1), self.vtol_angle)
            )

        pusher = self.doc.getObject("PusherRotor")
        pusher.Placement = App.Placement(
            PUSHER_PIVOT, App.Rotation(App.Vector(1, 0, 0), self.pusher_angle)
        )

        control = self.doc.getObject("AnimationController")
        control.Phase = state["phase"]
        control.Frame = self.frame
        control.Progress = 100.0 * progress
        control.Altitude_m = state["altitude"]
        control.Distance_m = state["distance"]
        control.Speed_mps = state["speed"]
        control.FrontTilt_deg = state["front_tilt"]
        control.RearTilt_deg = state["rear_tilt"]
        control.VTOL_RPM = round(state["vtol_rpm"])
        control.Pusher_RPM = round(state["pusher_rpm"])
        control.InterlockStatus = state["interlock"]

        self.doc.recompute()
        self.follow_camera(x, z)
        Gui.updateGui()

    def follow_camera(self, x, z):
        if coin is None:
            return
        try:
            camera = self.view.getCameraNode()
            camera.position = coin.SbVec3f(x + 6800, -7600, z + 4200)
            camera.pointAt(
                coin.SbVec3f(x + 1400, 0, z + 300),
                coin.SbVec3f(0, 0, 1),
            )
        except Exception:
            pass

    def step(self):
        progress = self.frame / float(TOTAL_FRAMES - 1)
        self.apply(progress)
        self.frame += 1
        if self.frame >= TOTAL_FRAMES:
            self.timer.stop()

    def start(self):
        self.timer.start()

    def pause(self):
        self.timer.stop()

    def reset(self):
        self.timer.stop()
        self.frame = 0
        self.vtol_angle = 0.0
        self.pusher_angle = 0.0
        self.apply(0.0)


doc = App.getDocument(DOC_NAME)
if doc is None:
    raise RuntimeError("Open CargoUAV_Refined_Flight_Animated.FCStd before running this macro")

if hasattr(builtins, "UAV_FLIGHT_ANIMATION"):
    try:
        builtins.UAV_FLIGHT_ANIMATION.timer.stop()
    except Exception:
        pass

builtins.UAV_FLIGHT_ANIMATION = FlightAnimation(doc)
builtins.UAV_FLIGHT_ANIMATION.start()
print("Flight animation started. Use builtins.UAV_FLIGHT_ANIMATION.pause(), .start() or .reset().")
