import sys, os


def main(argv):
	if len(argv) != 3:
		print "Usage"
		return 1
	
	ifname, ofname = argv[1:3]
	with open(ofname, "wb") as ofile:
		for line in open(ifname, "r"):
			if len(line) < 2:
				continue
			x, y, z = [int(x) for x in line.split(",")]
			ofile.write("%i,%i,%i\n" % (x - 5, y - 5, z - 5))
			ofile.write("%i,%i,%i\n" % (x, y, z))
			ofile.write("%i,%i,%i\n" % (x + 5, y + 5, z + 5))

if __name__ == "__main__":
	sys.exit(main(sys.argv))
