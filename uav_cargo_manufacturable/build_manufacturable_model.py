"""Build V-tail model with front-forward and rear-aft tilt at boom end."""

from pathlib import Path

HERE = Path(__file__).resolve().parent
source_path = HERE.parent / "uav_cargo_vtail_animation" / "build_vtail_tilt_model.py"
source = source_path.read_text(encoding="utf-8")
source = source.replace('P["rear_motor_x"]', '2000.0')
source = source.replace(
    'CargoUAV_HybridVTOL_VTail_TiltRotor_Animated.FCStd',
    'CargoUAV_HybridVTOL_Manufacturable.FCStd',
)
source = source.replace(
    'CargoUAV_HybridVTOL_VTail_TiltRotor_Animated',
    'CargoUAV_HybridVTOL_Manufacturable',
)
source = source.replace(
    'tilt_joint.CruiseAngle = -90',
    'tilt_joint.CruiseAngle = 90 if code.startswith("R") else -90',
)
namespace = {"__file__": str(Path(__file__).resolve()), "__name__": "__main__"}
exec(compile(source, str(source_path), "exec"), namespace)

