# SAR Cargo UAV

## Overview

**SAR Cargo UAV** is an engineering project focused on the development of a long-range unmanned aerial vehicle for **Search and Rescue (SAR)**, emergency logistics, and transport of critical payloads to remote or difficult-to-access locations.

The project explores a **fixed-wing / hybrid VTOL UAV architecture** designed to combine efficient long-range cruise performance with the operational flexibility of vertical takeoff and landing.

The current design target is a UAV capable of transporting approximately **5 kg of useful payload** over missions of up to approximately **400 km**, with emphasis on endurance, manufacturability, aerodynamic efficiency, operational safety, and field deployment.

---

## Mission

The UAV is intended to support operations such as:

- Search and rescue missions
- Emergency medical supply delivery
- Transport of medicines, blood bags, and medical equipment
- Delivery of food, water, radios, batteries, and survival equipment
- Support to isolated communities
- Disaster response
- Logistics in areas affected by floods, landslides, fires, or infrastructure failure
- Long-range autonomous cargo missions
- Support to remote industrial and mining operations

---

## Main Design Targets

| Parameter | Target |
|---|---:|
| Payload | ~5 kg |
| Mission range | Up to ~400 km |
| Aircraft type | Fixed-wing / Hybrid VTOL UAV |
| Propulsion | Gasoline-based cruise propulsion under evaluation |
| Takeoff / landing | Conventional and/or VTOL architecture |
| Navigation | Autonomous / GPS-assisted |
| Mission type | Cargo, SAR and emergency logistics |
| Design approach | Modular and manufacturable |

These values represent current engineering targets and may evolve during aerodynamic, structural, propulsion, and operational studies.

---

## Aircraft Architecture

Several configurations are being evaluated as part of the project.

Current concepts include:

- Fixed-wing cargo UAV
- Hybrid VTOL
- Tilt-rotor configurations
- V-tail configurations
- Safe transition between hover and forward flight
- Modular propulsion arrangements
- Manufacturable fuselage concepts

The objective is to identify the best compromise between:

- range;
- payload;
- endurance;
- aerodynamic efficiency;
- structural mass;
- propulsion efficiency;
- VTOL capability;
- reliability;
- manufacturing complexity;
- maintenance;
- operational safety.

---

## Engineering Workflow

The project uses an iterative engineering workflow combining CAD, simulation, scripting, and design reviews.

```text
Mission Requirements
        │
        ▼
Conceptual Design
        │
        ▼
Aircraft Geometry
        │
        ▼
FreeCAD Parametric Model
        │
        ├──► Structural / Packaging Assessment
        │
        ├──► Propulsion Integration
        │
        └──► Transition / Collision Analysis
        │
        ▼
CFD Geometry Export
        │
        ▼
OpenFOAM
        │
        ▼
Aerodynamic Analysis
        │
        ▼
Design Optimization
        │
        ▼
Manufacturable Configuration
```

---

## CAD

The aircraft geometry is being developed primarily using **FreeCAD**.

The repository includes scripts and macros used to generate and evaluate multiple aircraft configurations.

Areas currently under development include:

- fuselage geometry;
- wing geometry;
- V-tail;
- propulsion mounting;
- cargo compartment;
- VTOL propulsion;
- tilt mechanisms;
- component clearance;
- aircraft packaging;
- manufacturability.

Python automation is used extensively to generate and evaluate alternative geometries.

---

## CFD

Aerodynamic simulation is performed using **OpenFOAM**.

The CFD workflow is intended to evaluate:

- external aerodynamic flow;
- pressure distribution;
- lift;
- drag;
- aerodynamic efficiency;
- wake structures;
- propulsion-airframe interaction;
- aerodynamic effects of VTOL components;
- stability-related characteristics.

Typical workflow:

```text
FreeCAD
   │
   ▼
Geometry Export
   │
   ▼
STL / CFD Geometry
   │
   ▼
OpenFOAM Mesh
   │
   ▼
Flow Simulation
   │
   ▼
Aerodynamic Results
```

---

## VTOL Development

Hybrid VTOL configurations are being investigated to enable operations where conventional runways are unavailable.

Engineering studies include:

- rotor placement;
- tilt mechanisms;
- transition between hover and cruise;
- mechanical interference;
- propeller clearance;
- center-of-gravity effects;
- propulsion redundancy;
- safe transition trajectories.

Several scripts in the repository are dedicated to collision detection and transition studies.

Examples include:

```text
check_tilt_collisions.py
check_mirrored_tilt_collisions.py
sweep_rear_tilt_pivot.py
```

---

## Manufacturability

A major objective of the project is to evolve from conceptual aircraft geometry toward a configuration that can realistically be manufactured.

Design considerations include:

- composite structures;
- aluminum components;
- modular construction;
- removable wings;
- propulsion accessibility;
- maintenance access;
- cargo loading;
- landing gear;
- component standardization;
- assembly sequence;
- field repairability.

---

## Repository Structure

The repository currently contains engineering tools, models, documentation, and simulation environments.

Example structure:

```text
sar-cargo-uav/
│
├── openfoam/
│   └── CFD simulation cases
│
├── Tech Spec/
│   └── Technical specifications
│
├── uav_cargo_freecad/
│   └── FreeCAD models
│
├── uav_cargo_vtol/
│   └── VTOL configurations
│
├── uav_cargo_refined/
│   └── Refined aircraft geometry
│
├── uav_cargo_manufacturable/
│   └── Manufacturable configuration
│
├── uav_cargo_animation/
│   └── Aircraft animations
│
├── uav_cargo_safe_transition/
│   └── VTOL transition studies
│
├── assess_fuselage_layout.py
├── build_uav_vtol_headless.py
├── check_tilt_collisions.py
├── check_mirrored_tilt_collisions.py
├── export_manufacturable_cfd.py
├── sweep_rear_tilt_pivot.py
│
└── README.md
```

The directory structure may change as the project evolves.

---

## Main Tools

The engineering workflow currently uses:

- **FreeCAD** — parametric aircraft modeling
- **Python** — geometry generation and engineering automation
- **OpenFOAM** — computational fluid dynamics
- **Git / GitHub** — version control
- **PowerShell** — development environment automation
- **ParaView** — CFD visualization

---

## Design Priorities

The development follows several key priorities.

### 1. Mission capability

The UAV must be capable of transporting a meaningful payload over long distances.

### 2. Aerodynamic efficiency

Long-range missions require high lift-to-drag efficiency and careful aerodynamic optimization.

### 3. Operational flexibility

VTOL capability may allow operations without conventional runways.

### 4. Reliability

Search-and-rescue aircraft must prioritize predictable and fault-tolerant behavior.

### 5. Manufacturability

The design should be capable of progressing from a CAD concept to an aircraft that can realistically be manufactured and maintained.

### 6. Modular architecture

Subsystems should be replaceable and configurable whenever practical.

---

## Future Development

Planned engineering activities include:

- aerodynamic optimization;
- wing sizing refinement;
- propulsion sizing;
- gasoline engine evaluation;
- propeller optimization;
- VTOL propulsion sizing;
- fuel consumption modeling;
- center-of-gravity analysis;
- stability analysis;
- structural analysis;
- landing gear design;
- cargo compartment refinement;
- flight-control architecture;
- autopilot integration;
- telemetry;
- communication systems;
- mission planning;
- redundancy analysis;
- fail-safe architecture;
- prototype manufacturing;
- ground testing;
- flight testing.

---

## Project Philosophy

SAR Cargo UAV is being developed as an engineering platform rather than only as a single aircraft model.

The long-term objective is to build a modular design and simulation environment capable of supporting multiple UAV configurations for emergency logistics and autonomous cargo transportation.

The project combines:

**CAD + CFD + automation + simulation + manufacturing engineering + autonomous flight systems**

into a unified development workflow.

---

## Project Status

**Current phase:** Concept development / preliminary engineering.

The aircraft geometry,
