# Alpha Shape Processing Explanation
## Hagai Har-Gil, June 2020

## Technical Notes
1. I'm using Python 3.7 for all analysis and plotting.
2. I'm using the CGAL-based `cgal-python-bindings` Python package, presented to me by Dan and Efi, to calculate all alpha shape-related qunatities.
3. I'm using the version last committed on Apr 23, 18:31. This was the latest update Efi made which added a few CGAL objects I needed to interact with CGAL from Python.
4. [BTW, I guess Efi's contribution should be acknowledged in the article]

## Simulation
The script `simulate_alphashape.py` contains the simulations I made to visually verify my understanding of CGAL's results.

It starts by generating the following 3D pyramid:   
![Alpha pyramid](./alpha_shape_sim_pyramid.png)

The pyramid contains points, or `Point_3` objects, which will clearly be on the edge of any alpha shape, regardless of its radius (like the four outer edges on its base) and points which could be either inside or on the edges of the shape, depending on the size of the alpha shape radius. To receive a naive alpha shape object for these points, I simply call `alpha_shape = Alpha_shape_3(points)`.

The table below shows the coordinates and their alpha classification for different alpha values, which are written in the header. These alpha values were automatically generated using `alpha_shape.get_nth_alpha(idx)` for all available alpha values. To this list I made two changes: I changed the first alpha value to 0, since it was sometimes returned as a floating point number very close to 0, but not quite there, and I appended the "100.0" value to that list, just to make sure that the last alpha value which CGAL generated is indeed the biggest for that shape. Since the results in the "100.0" column are always equal to the last alpha value that was generated, I felt confortable with leaving it out when I ran the alpha computations on actual data.

The table below is a summary of the results for the simulation. You see how, for example, the first [0, 0, 1] point remains exterior to the shape for most iterations, but at that final alpha value it becomes "REGULAR", i.e. on the border of the alpha shape. The point below it, [0, 0, 0.5], becomes "INTERIOR" when it faces a large enough alpha value.

```
'coord',           0.0,    0.125,   0.3472,   0.875,    100.0 
0 0 1          EXTERIOR  EXTERIOR EXTERIOR   REGULAR   REGULAR
0 0 0.5        EXTERIOR   REGULAR  REGULAR  INTERIOR  INTERIOR
-1 0 0         EXTERIOR  EXTERIOR  REGULAR   REGULAR   REGULAR
1 0 0          EXTERIOR  EXTERIOR  REGULAR   REGULAR   REGULAR
0 1 0          EXTERIOR  EXTERIOR  REGULAR   REGULAR   REGULAR
0 -1 0         EXTERIOR  EXTERIOR  REGULAR   REGULAR   REGULAR
0 0 0          EXTERIOR   REGULAR  REGULAR   REGULAR   REGULAR
0.25 0.25 0    EXTERIOR   REGULAR  REGULAR   REGULAR   REGULAR
-0.25 0.25 0   EXTERIOR   REGULAR  REGULAR   REGULAR   REGULAR
0.25 -0.25 0   EXTERIOR   REGULAR  REGULAR   REGULAR   REGULAR
-0.25 -0.25 0  EXTERIOR   REGULAR  REGULAR   REGULAR   REGULAR
```

