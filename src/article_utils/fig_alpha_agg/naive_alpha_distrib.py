import pathlib

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from ncd_post_process.alpha_shapes import distance_alpha


neuron_names = [
    "AP120410_s1c1",
    "AP120410_s3c1",
    "AP120412_s3c2",
    "AP120416_s3c1",
    "AP120419_s1c1",
    "AP120420_s1c1",
    "AP120420_s2c1",
    "AP120510_s1c1",
    "AP120524_s2c1",
    "AP120614_s1c2",
    "AP130312_s1c1",
]


if __name__ == '__main__':
    foldername_alpha = pathlib.Path("/data/neural_collision_detection/results/with_alpha/")
    for neuron_name in neuron_names:
        alphas = distance_alpha.main_alpha_pipe(neuron_name, foldername_alpha)
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.hist(np.log(alphas + 1), bins=100)
        ax.set_title(neuron_name)
        ax.set_ylabel('Count')
        ax.set_xlabel('Log (alpha radius)')
        sns.despine(fig, trim=True)
        fig.savefig(f'results/with_alpha/{neuron_name}_alpha_naive_distrib.pdf', transparent=True)
