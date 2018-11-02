import matplotlib
import matplotlib.pyplot as plt
plt.switch_backend('agg')
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import numpy as np
import random

def plot_2d(value_array, output_filename, colormap = 'Reds'):
	dx, dy = 1, 1
	x_size = len(value_array)
	y_size = len(value_array[0])
	
	# generate 2 2d grids for the x & y bounds
	y, x = np.mgrid[slice(1, x_size + dy, dy),
					slice(1, y_size + dx, dx)]

	print (x_size, y_size)
	z = np.zeros((x_size, y_size))

	for i in range(x_size):
		for j in range(y_size):
			z[i,j] = value_array[i][j]

	# x and y are bounds, so z should be the value *inside* those bounds.
	# Therefore, remove the last value from the z array.
	z = z[:-1, :-1]
	levels = MaxNLocator(nbins=15).tick_values(z.min(), z.max())


	# pick the desired colormap, sensible levels, and define a normalization
	# instance which takes data values and translates those into levels.
	cmap = plt.get_cmap(colormap)
	norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

	fig, ax0 = plt.subplots(nrows=1)

	im = ax0.pcolormesh(x, y, z, cmap=cmap, norm=norm)
	fig.colorbar(im, ax=ax0)
	#ax0.set_title('pcolormesh with levels')
	ax0.set_title(colormap)


	# adjust spacing between subplots so `ax1` title and `ax0` tick labels
	# don't overlap
	fig.tight_layout()

	#plt.show()
	plt.savefig(output_filename)

	plt.close()
	

if __name__ == "__main__":
	z = []
	for i in range(20):
		z.append([])
		for j in range(30):
			val = -60
			if random.randint(0, 100) > 90:
				val = random.randint(20, 200)
			z[i].append(val)
			
	plot_2d(z, "try.png")
	
	
