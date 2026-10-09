# CAD

Parametric source in `src/umi` (build123d). All dimensions live in `src/umi/params.py`.

```bash
conda create -n umi-cad python=3.12 && conda activate umi-cad
pip install -r cad/requirements.txt
cd cad/src
python -m umi.check     # stroke sweep: gears, carriages, frame
python -m umi.build     # all parts -> cad/STEP, cad/STL (+ assemblies) and interference report
python -m umi.render    # previews -> docs/img
```

| Folder | Parts | Qty |
|---|---|---|
| `jaw_module/` | `frame`, `carriage`, `pinion` | 1, **2**, 1 |
| `collector/` | `finger_ring_thumb`, `finger_ring_index`, `pod`, `pod_lid`, `magnet_cap` | 1 each |
| `openarm_unit/` | `servo_cradle`, `servo_cradle_lid`, `horn_coupler` | 1 each |
| `cameras/` | `cam_imx335_mount`, `cam_d405_cradle` | pick one |

`third_party/` holds the HandUMI tips and YUBI OpenArm flange, unmodified, with their licenses.
`tools/inspect_step.py` prints holes and bosses of any STEP file and was used to measure the reference parts.

## Assemblies (`cad/assemblies/`)

`python -m umi.export_assembly` writes the collector and OpenArm unit, each at full open (80 mm) and nearly closed (10 mm),
with rods, bearings and the HandUMI UMI-Gripper tips included, one named and coloured part each:

| File | Use |
|---|---|
| `*.step` | **Onshape** (Create → Import): imports as editable, named parts in mm |
| `*.gltf` | Onshape mesh import (view only), or any glTF viewer |
| `*.glb` | Single-file glTF for web viewers, Blender, etc. Onshape doesn't list `.glb` as an import format |

glTF/GLB are in metres (glTF convention); STEP is in millimetres. The servo is shown as its measured envelope.
