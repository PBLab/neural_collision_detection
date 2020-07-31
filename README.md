# Neural Collision Detection Documentation

The software presented here is designed to detect and analyze collisions in 3D space between two objects. In the [accompanying article]() the target objects were the vascular network of a part of the cortex of a mouse and a specific type of neurons that are usually found in close interaction with it. The goal was to provide a null hypothesis to questions that deal with the distribution of distances between this neuron population and the vasculature. Be that as it may, this work is applicable to other questions and problems, although in that case many of the analysis scripts won't be of use to the users.

### The problem

Given some vascular data and a neuron in a specific location, we want to efficiently minimize the number of collisions between two objects by rotating the neuron around its axes. After aggregating all of the optimal rotation-location pairs we'd like to characterize the statistical properties of these collisions in regards to their location on the neuron and on the vasculature, since we consider the small number of collisions that "survived" the minimization process as possible interaction points between the neurons and vasculature.

### The solution - `ncd`

Here we introduce a program named `ncd` (Neural Collision Detection) which is a wrapper over the powerful [`fcl`](https://github.com/flexible-collision-library/fcl) that eases the analysis of collisions between vasculature and neurons. At itsc core, `ncd` computes the number of collisions between the two objects for all possible rotations.

Usage information can be found in the `docs` folder of the repo.

