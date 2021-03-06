------------
Ongoing Work
------------
* I divided the collision figure into two parts - 3D Viz and aggregation.
  They're now in their own folders under ``article_utils``.

* The rest of the figure is made out of previous scripts - alpha vs dist, alpha
  vs collisions.

* I added a ``fig_alpha`` folder under the ``for_article`` folder which
  contains the code for this figure. The first file there is a file that
  shows the distribution of the alpha shape values for each neuron.

* We fixed this issue and re-ran the NCD computation. This data is in the Sep 
  5th folder.

* Another bug I witnessed has to do with the locations that NCD decides are the
  best for each neuron. NCD chooses location right on the edge of the vasculature
  every time since it has the fewest collisions.

* The MW120607_LH3 neuron is too long to fit into our vasculature so we discard
  it from our computational pipeline.

* What files did I run after the basic pipeline was completed?
        - collisions_vs_dist_naive
        - distance_alpha
        - find_block_properties
        - correlate_coll_alpha
        - show_collisions_dist
        - overlay_collisions_napari
        - alpha_vs_density
        - alpha_vs_topodist
        - collision_distribution
        - neuron_to_vasc_dist_distrib

 * I also added to the docs the fact that we need to run the alpha shape pipeline
  in addition to the rest of the functions.

* After a lot of testing and I discovered a bug with the way the neurons are
  represented in 3D - the Y and Z axes were flipped, which caused the issues
  with the display that we had. I had to fix it, together with Yoav, from the
  "roots" of NCD by changing the MATLAB code that generated the objects NCD was
  colliding. This took a while to track and a longer while to run.

* I sometimes see a bug where a 3D shape becomes "2D", or flat in 3D. This
  happens when I switch between columns in an array but don't copy them first.

* I haven't succeeded in rotating and translating the vasculature, a neuron and
  its collision to the same coordinate system. Thus I started writing proper
  tests for this part which should help me decompose the issue.

* I found a small miscalculation in the collision normalization step. I fixed
  it and re-ran all of the normalization and graphing processes again.

* I created figure 2 and added the missing panels to it.

* I improved the layout of result files and divided them into folders.

* I updated the analysis scripts of the collision vs distance jointplots to make them run with the
  new folder structure and the new ideas we had regarding figure 2.

* Another "missing" correlation is between U(r) and the alpha value. The results are in ``for_article
  /fig2`` and show that even for low alpha values the distribution of U(r) is quite large, which
  is a bit surprising.

* I added a couple of functions in ``alpha_shapes/alpha_vs_topodist.py`` that plot a scatterplot
  of alpha values vs topological distance just to see whether there's any correlation. As expected,
  it's not too strong but there's a slight upwards trend, meaning that the further away you
  are from the soma the higher you alpha value is.

* We tried to identify the direct connection between collision and alpha values in ``correlate_
  coll_alpha.py``. We're looking at the entire neuron and plotting the relations of collisions
  and alpha values per axon\dendrite. We also normalize these aggregated probabilities with
  the topological length of the neuron. We see that the axons' collision probability remains
  fixed throughout its length, while dendrites are less fixed and more variable.

* I took from the table of all pairs of proximal axons and dendrites, found in ``distance_
  alpha.py``, two groups - the mostest closest pairs, and all other pairs, and tried to plot
  them together to see if the distribution of the mostest closest looks different than the
  distribution of the other group. The result was no - there's not visible difference.

* Using ``find_block_properties.py`` in the ``alpha_shapes`` module I was able to divide
  each neuron into many bounding boxes and visualize their collision and alpha distribution
  successfully. This didn't reveal too much, since the correlation between the alpha shape
  and the collision chance isn't quite clear yet. Be that as it may, we're at least able to
  view these boxes in 3D on top of the neuron in Blender, which is definitely progress.
  To the rescue came a fixed version of ``draw_bounding_boxes.py``.

* I added code that divides the space into blocks and calculates properties of each box
  separately. I tried visualizing these boxes with blender ``blender/draw_bounding_boxes.py``
  but it doesn't look too well. I need to draw individual boxes.

* I added the new alpha shape values to the neuronal graphs (made with ``graph_parsing.py``)
  and also updated some of its code to use float32 instead of 64.

* The package `pywavefront` allows me to read Blender-generated meshes
  easily and reliably, which look much better than the ones we made earlier.
  Use with: ``wf = pywavefront.Wavefront(fname, collect_faces=True)``

* To better understand the distribution and differences between the alpha shape value
  and the collision chance, I will use a 3D window function to assess the distribution
  of the two in each of these blocks. The resulting plot is a jointplot where the first
  axis is the coll chance, the second is the alpha value, and the dendrites and axons
  are colored differently.

* I decided to filter the pairs of axon-dendrites to only ones that are no more than
  50 um apart in the first place, to avoid looking at very distal parts of the axonal
  tree which clearly have no proximal dendrites. I also changed the quantile to 0.95
  due to the previous change.

* ``distance_alpha.py`` generate HDF5 files which end with ``*closest_pairs.h5`` and
  contain a DataFrame with the 20 nearby pairs of axons and dendrites, as well as the
  distance between them (in um), the collision prob. of each point and the alpha value
  of each of them. The data actually is only the 99th quantile of the "collision delta",
  i.e. only the points that were truly close and were truly different in their collision
  probabilities were checked. We're talking about 1000 points.

* In ``distance_alpha.py`` I added code that finds nearby axons and dendrites and compares
  their collision and alpha shape values. I hope to find nearby axon-dendrite pair with
  a large difference between their collision probabilities - and also a large difference
  in their alpha shape value.

* I created a table for each neuron in `results/for_article/fig2` where each row
  is a collision point, and each column's header is the alpha shape value that was
  used to calculate the relation of that point to the alpha shape. The relation
  values are as follows:
  ``cls_dict = {
        "INTERIOR": np.int8(0),
        "EXTERIOR": np.int8(1),
        "REGULAR": np.int8(2),
        "SINGULAR": np.int8(3),
    }``

* How did I compile the Python bindings for CGAL:
  1. Cloned the repo to ``/data/MatlabCode/PBLabToolkit/External/cgal-python-bindings``.
  2. ``mkdir build && cd build``
  3. Used one of the shell scripts in the "scripts_for_cgal" folder here to compile
     a specific binding.
  4. Copied the generated ``tri3_epic.so`` to its own folder under ``src/alpha3_bindings``.
  This file can be imported as a standard Python module.

* The COVID outbreak halted the project for quite some time, and other difficulties
  also made it slow down. I tried using Alpha shapes in Python and MATLAB but
  the algorithms there weren't implemented well enough, and I had many curious
  results which I couldn't explain. Sadly we decided, after an online meeting we
  had, to use CGAL, which is the state of the art computational geometry toolbox,
  written in C++ of course. Since there were no available suitable bindings for
  the CGAL modules that deal with Alpha shapes in 3D, we had to ask Efi Fogel,
  who works with Dan, to generate these bindings for us. It took some time for both
  us and him to reach a working prototype - but it finally happened, and now I can
  import into Python some of the alpha shapes capabilities of CGAL.

* In preparation for the 23/2/2020 meeting I changed the way we calculate the
  probabilities as listed below. We decided to also dive a bit deeper to try and
  find out why the collision probablities of dendrites and axons are so different
  even when they're nearly co-localized.

* After the latest meeting I re-ran NCD again on the neurons due to a change we
  did to the binary - we're now only capturing the best orientation in each
  location, and not the top 10. This was done to improve our calculation for
  the probability of collision per point. We're also now normalizing the probability
  by the number of actual locations NCD returns, and not by the theoretical number
  that NCD tested. Additionally, we've rounded the collision coordinates into the
  nearest integer, since the added floating point precision is due to computational
  artifacts. Finally, we've added this new information - better collision coords and
  the correct collision probability into the graph of every neuron.

* I tried re-running the analysis pipeline on the two layer II/III neurons that
  show a very low number of collisions (507 and 131) and it seems that this
  result stands. Not sure what to make of it.

* In ``show_collisions_dist.py`` I tried to look at the cumulative sum of the collisions,
  to see if I detect any pattern in the distributions of neurons in different
  layers, but I couldn't find such. The average running sum of the neurons in II/III
  vs. the rest also didn't reveal much.

* I completed the work on the first figure and the two supplemental figures
  that accompany it - one of the computational pipeline and the other of the
  different type of toy neuron that tests the collision numbers. The code is
  now in ``src/article_utils/`` while the data it uses and generates is in
  ``results/for_article``.

* I detected a bug in the topological distance caluclation - I wasn't handling
  correctly the cases in which there's a large jump between one point to the
  next one, which caused the calculated distance values to be way too big.
  I fixed it in ``graph_parsing.py``, and re-ran all of the scripts using the
  distance data. In addition I re-wrote the collisions vs distance plot inside
  ``collisions_vs_dist_naive.py``.

* I created a mock fig2 file ("fig2mock.svg") that describes the way we want
  to see figure 2 in the article. It's slightly different than the current one,
  although it uses mostly the same data.@

* The script ``for_article/fig1/find_collisions_distribution.py`` generates
  an image of the toy neuron with the probability of collisions overlayed
  on top of it. In the process of making it we found that the smaller branches
  of the neuron collided less with the vasculature. This may be the result of
  the scale of these branches being smaller than the typical distance between
  the vascular pipes in the toy data. Thus we'll be running ncd on the toy
  case but with different spaces between vascular grids. We'll then make a fig,
  possibly a supp, with the different collision distributions on top of the
  neuron with different typical vascular distances. We'll calculate the mean
  size of the neuron in its last segment (possibly using fractals) and show
  that whenever that neural distance is less than the distance between two
  vascular pipes in the grid, the chance for a collision in these distal areas
  of the neuron is minimal.

* I was able to finally make the ``overlay_collisions.py`` script work in
  Blender 2.80 (as well as 2.79), but it came at a cost of corrupting the
  existing ``artificial_neuron.obj`` file that was created. So I had to
  make a new one (git didn't track it) and run NCD on it. The real issue
  was with the data that was created by NCD - the collisions were probably
  too far off, so Blender just placed them in the center. They were also
  not rotated, it seems. This is why it was a good idea to re-run the pipeline
  with the newly generated obj.

* I made changes to ``collisions_vs_dist_naive.py``, and it now can create
  the hexbin plots of all neurons one after the other, i.e. not jointplots.
  This is for the second part of figure 2. I'm also currently not aggregating
  the histograms in this figure, since I simply wasn't able to. I created a
  jupyter notebook and an "AggregatedData" class. I deleted the class and
  the notebook is currently not used for anything.

* I decided to discard one neuron, "AP131105_s1c1", due to a very low collision
  number which hinders its statistics and visualization.

* I created the base for figure 2 in the article from code in
  ``collisions_vs_dist_naive.py``. It's a class which runs on existing
  graphs generated in ``analyze_graphs.py``, and finds and plots the
  density of the collisions as a function of the topological distance.
  This class now correctly calculates the "neural density" and normalizes
  the collision counts by them. For the two large plots I used neurons
  "AP130312_s1c1" (layer 2/3) and "AP120412_s3c2" (layer 5).

* Pablo wants me to check the "neural density". This metric checks how much
  "neuron" exists at at a certain distance from the soma. We expect that if
  a neuron's density is increased at some topological distance d, at that
  d the number of collisions will also increase.

* I also made many corrections to the manuscript that Yoav started.
  I labeled the versions before major changes.

* Discussion items for next meeting:
  1. How to show in the toy example that our pipeline detects orientation
  correctly? Should we show the neuron on pipes toy example? Discuss the
  statistics I used (Shapiro Wilk).
  2. How should the figure showing the distribution of collisions over time
  look like?
  3. Describe each figure we currently have.

* The ``for_article`` folder contains the needed figures and code for figure 1.
  I also wrote a few scripts to process the data that was generated by Yoav
  for these figures, which are located in the code folder. The shell scripts
  that ran the aggregation and NCD itself can also be found there.

* I created a folder named ``for article`` in the ``results`` folder, and made
  an ``svg`` with all of the figures for all of the neurons in a table, sorted
  by their cortical layer. Layer 2/3 neurons always show a spike in their
  axonal collisions vs distance plot, while the other neurons show a flat
  graph.

* I re-ran ``ctp2mesh.mat``, ``write_mesh_to_disk.m`` and ``csv_to_obj.py``
  to make sure that vascular object we've been working with is indeed the
  full object that can be created. It is indeed the case.

* The latest advancement in the collisions business is achieved in the class
  :class:`ncd_post_process.collisions_as_func_of_dist.CollisionsAndDistance`.
  This class takes an existing neuronal graph and adds information for each of
  the nodes about the closest collisions that are around it. However this is not
  done simply by comparing the distance between all collisions and all nodes.
  Instead, the algorithm finds the 5 closest points on the neuron to that
  collision and interpolates them so that there's a smoother surface
  between the neuron and the collision. Then it uses this new surface to
  calculate the distance.

* Following the April 3rd meeting we've come to realize that the original
  collision data that is generated in FCL is not using any interpolation, which means
  that the interpolation step described above is useless - it's overfitting
  the collision location. We will currently stay with the original implementation of
  the number of collisions as a function of distance which is located in
  ``collisions_vs_dist_naive.py``.

.. image:: work.jpg

* Following another meeting with Pablo on the 13 of May (image from the meeting),
  we decided to conduct the following analysis steps: Generate a "Neuron ID"
  document, which consists of several figures that are assigned to each neuron
  in our list:

  1. An image derived from Neurolucida's XML tree.
  #. An image of the mesh object as was received by FCL.
  #. A visualization of the neuron from Blender showing the collisions overlayed
     on the different neurites. The colors should resemble the original paper
     (blue is axon, orange is dendrite) and the actual way to represent the
     collisions might either be with a blob or by coloring the actual neuronal
     surface.
  #. A graph showing the number of collisions as a function of the topological
     distance.
  #. A graph showing the number of collisions as a function of :math:`U_n(r)`,
     which is the number of points on the neuron encompassed by a sphere with
     radius :math:`r` centered around a point on the neuronal tree. The graph
     should contain data from multiple :math:`r` values in different colors.
  #. A graph showing the number of collisions as a function of :math:`U_v(r)`,
     the total volume of the vasculature encompassed by a sphere with radius
     :math:`r` centered around a point on the neuronal tree.
  #. A scatter plot showing the values of :math:`U_n(r)` and :math:`U_v(r)` as
     a function of the topological distance of that point.
  #. 3D scatter plot for each point on the neuronal tree showing its assigned
     number of collisions, :math:`U_n(r)` and :math:`U_v(r)`.

  The code for these figures will be located in ``ncd_post_process/create_neuron_id``.

* The code in ``ncd_post_process/create_neuron_id/compare_collisions_with_density.py``
  creates a scatter plot of the number of collisions as a function of the
  density of a given neuronal point (shown below). We sometimes see two
  population of points on the dendritic tree - the lower and upper one. We see
  that the more complex a neural point is, the less likely it is to encounter
  a blood vessel.

.. image:: coll_dens.png

* Due to the two populations which are visible in the scatter plot, we wish
  to display the points of that upper cloud on a neuron, probably using Blender.
  We'd also like to change the scale of the y-axis, so that it would show the
  "probability of collision", i.e. the fraction of collisions a point experienced
  out of the total iteration steps it has undergone. The scale of the y-axis will
  be [0, 1], with 1 being a 100% chance to collide with a blood vessel in every
  iteration (= neuron orientation).

* In May 26 I updated the y-axis of ``ncd_post_process/create_neuron_id/compare_collisions_with_density.py``
to be P(collision). This is calculated by dividing the number of collision by
100k, since we currently have 10k locations per cell, and we keep the data from
10 orientations.

* Meeting with Dan @ 26.5:

    1. Show the collisions on the neurons with Blender.
    #. Re-run NCD with lower collision thresholds, i.e. only permit locations
       and orientations that contain 20, 40, 50 collisions in total.
    #. Yoav will calculate :math:`U(r)` for all points on the vascular tree, for
       multiple :math:`r`s. Once he does that we want to match between each
       collision and its closest point on the vascular tree, essentially
       creating a mirror image of the collisions on top of the vasculature.
    #. The 3D scatter plot mentioned above is also important in understanding
       the relations between the points on the neuronal tree.
    #. Add to the scatter plots the distribution of the points on each axis.

* As a preparation for the upcoming 26.6 meeting, I've created a mini-ID PDF
figure for each neuron. The PDF contains a plot of the numbers of collision as
a function of :math:`U(r=10)`, with the distributions of :math:`U(r)` and the # collisions
on each side. It also contains a Blender render of the neuron with 3 axial
projections of the neuron overlayed with the number of collisions it felt
on each pixel. All plots were generated manually in Blender, with py3DN
and :class:`blender/overlay_collisions.py`.

* For the same meeting, I also added the method ``get_top_colls_percentile`` to
:class:`BranchDensityAndCollisions` as a way to save to disk only the locations
that had the highest chance to collide with blood vessels. I then followed by
using Blender to show the collisions on top of each neuron. It seems that
for the most part, these locations are on
 the dendritic tree of the neuron,
rather than on its axon.

* Yoav supplied the file ``calc_u_for_vascular.py`` which returns the :math:`U(r)`
value for each point on the vascular tree. The script takes
about 90 minutes to run for a single :math:`r` on Cortex. The next step is
to pair each collision with the appropriate :math:`U(r)` value, just like
I did for the neurons.

* In ``compare_collisions_with_density.py`` I added a function :func:`run_ur_topodist()`
which creates an instance of the class :class:`BranchDensityAndDist` which
ultimately plots the density :math:`U(r)` as a function of the topological
distance of a given point on the neural tree. The same trendline that appears
in the r=10 case is prominent in smaller R's as well.

* In ``compare_collisions_with_density.py`` I added a function
:func:`run_collisions_dens_jointplot_multiple_r()`
which plots the collisions as a function of density jointplot for a single
neuron with multiple R's (for :math:`U(r)`). The "double hump" trend is visible in
the different R's as well, suggesting that it's not an artifact of the r=10
measurement, but a true characteristic of the distribution.

* I installed blender at ``~/blender-2.79b-...`` to visualize large vascular
3D models.


