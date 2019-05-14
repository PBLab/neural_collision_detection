------------
Ongoing Work
------------

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
