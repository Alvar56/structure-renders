"""Render a consistent series of protein figures with ChimeraX.

Every figure shares one house style (soft ambient-occlusion lighting, dark outline,
sage-green cartoon, one amber highlight) and is described by a short recipe below:
which PDB entry to fetch, what to remove, what to highlight and how to orient it.

    chimerax --nogui --offscreen --script "scripts/render.py"           # all figures
    chimerax --nogui --offscreen --script "scripts/render.py ccr5"      # one figure

Raw PNGs are written to build/; run scripts/frame.py afterwards to crop them onto
identical 16:10 canvases in figures/.
"""
import os
import sys
from chimerax.core.commands import run

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BUILD = os.path.join(ROOT, 'build')
os.makedirs(BUILD, exist_ok=True)

GREEN, GREEN_DARK, GREEN_LIGHT, AMBER = '#7fb276', '#4f8a52', '#a9cf96', '#e8a93a'

STYLE = [
    'windowsize 1600 1000',
    'set bgColor white',
    'lighting soft multiShadow 512 msMapSize 2048 depthCue false',
    'graphics silhouettes true width 2 color #24352a depthJump 0.02',
    'material dull',
]

FIGURES = {
    # Chemokine receptor CCR5 with the HIV entry inhibitor maraviroc in its pocket.
    'ccr5': {
        'pdb': '4mbs',
        'prepare': ['delete /B', 'delete ligand & ~:MRV', 'delete protein & :1000-1099'],
        'colour': [f'color protein {GREEN} target c'],
        'ligand': ':MRV',
        'turns': ['turn x -90', 'turn y 30', 'view', 'turn z 90'],
    },
    # Cellulose synthase homotrimer with the glucan chains it extrudes.
    'cesa': {
        'pdb': '6wlb',
        'prepare': [],
        'colour': [f'color /A {GREEN} target c', f'color /B {GREEN_DARK} target c', f'color /C {GREEN_LIGHT} target c'],
        'ligand': ':BGC',
        'turns': ['turn x -90'],
    },
    # Salmonella flagellin; the variable D3 domain that defines the serotype in amber.
    'flagellin': {
        'pdb': '1io1',
        'prepare': ['delete ligand'],
        'colour': [f'color #1 {GREEN} target c', f'color #1 & strand {GREEN_DARK} target c',
                   f'color #1 & :190-290 {AMBER} target c'],
        'ligand': None,
        'turns': [],
    },
    # ATG12-ATG5-ATG16N, the complex that attaches ATG8 to membranes.
    'atg16': {
        'pdb': '4gdk',
        'prepare': ['delete ligand', 'delete /D-F'],
        'colour': [f'color /A {AMBER} target c', f'color /B {GREEN} target c', 'color /C #2f6b38 target c'],
        'ligand': None,
        'turns': ['turn y 70'],
    },
}


def render(name, fig):
    run(session, 'close session')
    for c in STYLE:
        run(session, c)
    run(session, f"open {fig['pdb']}")
    run(session, 'delete solvent')
    for c in fig['prepare']:
        run(session, c)
    run(session, 'hide atoms; hide pbonds; label delete')
    run(session, 'cartoon')
    run(session, 'cartoon style width 2.0 thick 0.55')
    for c in fig['colour']:
        run(session, c)
    if fig['ligand']:
        lig = fig['ligand']
        run(session, f'show {lig} atoms; style {lig} sphere; color {lig} & C {AMBER}')
        run(session, f'color {lig} & N #3a64c4; color {lig} & O #d2493a; color {lig} & F #7cc8db')
    run(session, 'view')
    for c in fig['turns']:
        run(session, c)
    run(session, 'view')
    run(session, 'lighting depthCue false')
    out = os.path.join(BUILD, f'{name}.png').replace('\\', '/')
    run(session, f'save "{out}" width 1600 height 1000 supersample 3')


wanted = [a for a in sys.argv[1:] if a in FIGURES] or list(FIGURES)
for name in wanted:
    render(name, FIGURES[name])
run(session, 'exit')
