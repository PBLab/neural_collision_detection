#!/bin/bash
#PBS -e /tmp/pblab/matlab/output
#PBS -o /tmp/dvory/matlab/output

matlab -nodisplay -r /data/neural_collision_detection/src/article_utils/fig2/run_alpha_shape_for_all_neurons.m
