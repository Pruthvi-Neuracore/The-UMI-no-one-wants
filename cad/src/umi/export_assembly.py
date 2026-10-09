"""Export named, coloured assemblies for viewing / importing elsewhere (e.g. Onshape).

    python -m umi.export_assembly     # -> cad/assemblies/{collector,openarm_unit}_{open,closed}.{step,glb,gltf}

STEP keeps one named solid per part (imports into Onshape as editable parts).
GLB/glTF are meshes in metres (glTF convention), one named node per part.
"""
from pathlib import Path

import numpy as np
import trimesh
from build123d import Color, Compound, export_step

from .build import PARTS, assembly
from .render import colour, vitamins
from .params import TRAVEL

OUT = Path(__file__).resolve().parents[2] / "assemblies"


def mesh(part, rgb):
    verts, tris = part.tessellate(0.1, 0.2)
    v = np.array([(q.X, q.Y, q.Z) for q in verts]) / 1000.0           # mm -> m
    m = trimesh.Trimesh(v, np.array(tris), process=False)
    m.visual = trimesh.visual.ColorVisuals(m, face_colors=np.tile([*rgb, 255], (len(tris), 1)))
    return m


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    parts = {k: fn() for k, (fn, _, _) in PARTS.items()}
    for kind in ("collector", "openarm_unit"):
        for opening, tag in ((2 * TRAVEL, "open"), (10.0, "closed")):
            a = assembly(kind, opening, parts) | vitamins(opening)
            children, scene = [], trimesh.Scene()
            for name, p in a.items():
                hexc = colour(name).lstrip("#")
                rgb = [int(hexc[i:i + 2], 16) for i in (0, 2, 4)]
                p = p if hasattr(p, "label") else Compound(p)
                p.label, p.color = name, Color(*[c / 255 for c in rgb])
                children.append(p)
                scene.add_geometry(mesh(p, rgb), node_name=name, geom_name=name)
            stem = OUT / f"{kind}_{tag}"
            export_step(Compound(children=children, label=f"{kind}_{tag}"), str(stem.with_suffix(".step")))
            scene.export(str(stem.with_suffix(".glb")))
            scene.export(str(stem.with_suffix(".gltf")), embed_buffers=True)
            print(stem, len(children), "parts")


if __name__ == "__main__":
    main()
