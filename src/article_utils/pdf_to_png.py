import subprocess
import pathlib


foldername = pathlib.Path('/data/neural_collision_detection/results/with_alpha/')
assert foldername.exists()
for file in foldername.glob('alpha_vs_*.pdf'):
    new_fname = str(file)[:-4]
    subprocess.run(['pdftoppm', str(file), new_fname, '-png'])

