# OpenFOAM mesh-family campaign

Date: 2026-09-27  
OpenFOAM: v14  
Solver: `foamRun` / `incompressibleFluid`  
Run configuration: 1,000 iterations, 10 MPI ranks, 25 m/s, 4 degrees angle of attack

## Results

The coefficient statistics use the last 100 samples (iterations 901 through 1,000).

| Mesh | Cells | Cd mean | Cl mean | Cm mean | Solver ClockTime | Full wall time | Peak RSS | Airframe y+ avg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Coarse | 636,401 | 0.0300305 | 0.286329 | -0.0099682 | 548 s | 11:00.88 | 816 MiB | 48.89 |
| Medium | 937,219 | 0.0290444 | 0.298557 | -0.0058650 | 829 s | 15:47.80 | 1,177 MiB | 42.78 |
| Fine | 1,554,300 | 0.0261712 | 0.296100 | -0.0048309 | 1,411 s | 25:27.90 | 1,770 MiB | 36.66 |

All three meshes passed `checkMesh`.

| Mesh | Maximum non-orthogonality | Maximum skewness | Airframe layer coverage |
|---|---:|---:|---:|
| Coarse | 63.88 deg | 2.524 | 89.9% |
| Medium | 64.41 deg | 1.993 | 91.2% |
| Fine | 63.34 deg | 3.262 | 92.8% |

## Interpretation

- Lift is approaching mesh independence: medium differs from fine by only +0.83% in `Cl`. Coarse is 3.30% below fine.
- Drag is not mesh-independent: medium is 10.98% above fine and coarse is 14.75% above fine. A fourth, finer mesh or targeted wake refinement is required before treating `Cd` as converged.
- Pitching moment remains strongly mesh-sensitive because its magnitude is small: medium differs from fine by 21.4%, while coarse differs by 106%. Do not use the coarse `Cm` for design decisions.
- Airframe average `y+` improves monotonically from 48.9 to 36.7. This is suitable for a wall-function RANS study, but the local range remains broad. It is not a wall-resolved result.
- Runtime scales reasonably with size. Relative to coarse, medium has 1.47 times as many cells and needs 1.51 times the solver clock time; fine has 2.44 times as many cells and needs 2.57 times the time.
- For iteration and lift studies, medium is the best cost/accuracy compromise. For drag and moment, the present fine mesh is a better baseline but is not yet a demonstrated mesh-independent solution.

## Geometry limitation

The exported watertight STL contains the airframe, nacelles and aft pusher geometry. The partitioning pass found no triangles belonging to the four lift-rotor blade volumes at their expected positions. Consequently, these simulations do **not** include the aerodynamic effect of the four tilt-rotor blades. This must be corrected in the CAD export before interpreting the result as a complete powered-aircraft model.

## Reproduction

Each case retains `0.orig`, `constant`, `system`, `Allmesh`, `Allrun`, the final reconstructed state and post-processing data. Run `summarize_results.py` from this directory to regenerate the numerical summary from the retained logs and coefficient histories.
